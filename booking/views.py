import stripe
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import generics
from .serializers import *
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from django.conf import settings
from django.shortcuts import redirect

# Create your views here.

stripe.api_key = settings.STRIPE_SECRET_KEY
webhook_secret = settings.STRIPE_WEBHOOK_SECRET


class AvailableView(APIView):
    def get(self, request):

        associate_id = request.query_params.get("associate_id", None)
        print(associate_id, "id received")
        if associate_id:
            availabilities = Available.objects.filter(associate=associate_id)
        else:
            availabilities = Available.objects.all()
        serializer = AvailableSerializer(availabilities, many=True)
        for data in serializer.data:
            associate_id = data[
                "associate"
            ]  # Assuming associate_id is present in the serializer data
            associate_instance = Associate.objects.get(id=associate_id)
            associate_serializer = AssociateSerializer(associate_instance)
            data["associate"] = associate_serializer.data
        return Response(serializer.data)

    def post(self, request):
        print("date", request.data.get("date"))
        date = request.data.get("date")
        associate_id = request.data.get("associate")
        noon = request.data.get("is_noon")
        morning = request.data.get("is_morning")

        query = Q(date=date, associate=associate_id) & (
            Q(is_morning=morning) | Q(is_noon=noon)
        )
        instances = Available.objects.filter(query)
        if instances:
            return Response(
                {"error": "exists on this shift"},
                status=status.HTTP_409_CONFLICT,
            )

        existing = Available.objects.filter(
            date=date, associate=associate_id, is_morning=True, is_noon=True
        ).exists()
        if existing:
            return Response(
                {"error": "A slot already exists on this day"},
                status=status.HTTP_409_CONFLICT,
            )

        existing_instance = Available.objects.filter(
            date=date, associate=associate_id, is_morning=morning, is_noon=noon
        ).exists()

        if existing_instance:
            return Response(
                {
                    "error": "A slot with the same date and associate already exists."
                    # "error": "An instance with the same date and associate already exists."
                },
                status=status.HTTP_409_CONFLICT,
            )

        serializer = AvailableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def delete(self,request):



# @api_view(["POST"])
# def test_payment(request):
#     test_payment_intent = stripe.PaymentIntent.create(
#         amount=1000,
#         currency="pln",
#         payment_method_types=["card"],
#         receipt_email="test@example.com",
#     )
#     return Response(status=status.HTTP_200_OK, data=test_payment_intent)


class StripeCheckout(APIView):
    def post(self, request):
        print(request.data)
        # dataDict = dict(request.data)

        # price = dataDict['price'][0]
        price = request.data.get("payable_amount")
        print(price)
        # product_name = dataDict['product_name'][0]
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": "slot booking",
                            },
                            "unit_amount": price,
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url="http://localhost:3000/secured/success",
                cancel_url="http://localhost:3000/secured/failed",
            )
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            print(e)
            # return e
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class Webhook(APIView):
    def post(self, request):
        event = None
        payload = request.body
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]

        print("webhook")
        print(stripe_webhook_secret)
        print(sig_header)

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except ValueError as err:
            # Invalid payload
            raise err
        except stripe.error.SignatureVerificationError as err:
            # Invalid signature
            raise err

        # Handle the event
        if event.type == "payment_intent.succeeded":
            payment_intent = event.data.object
            print("--------payment_intent ---------->", payment_intent)
        elif event.type == "payment_method.attached":
            payment_method = event.data.object
            print("--------payment_method ---------->", payment_method)
        # ... handle other event types
        else:
            print("Unhandled event type {}".format(event.type))

        return JsonResponse(success=True, safe=False)
