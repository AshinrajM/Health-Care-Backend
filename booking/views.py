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
from django.http import JsonResponse


# from corsheaders.response import SuccessMessageResponse
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


class StripeCheckout(APIView):
    def post(self, request):
        print(request.data)
        price = request.data.get("payable_amount")
        user_id = request.data.get("user_id")
        slot_id = request.data.get("slot_id")

        print(request.data)

        print(price)
        # product_name = dataDict['product_name'][0]
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        "price_data": {
                            "currency": "inr",
                            "product_data": {
                                "name": "slot booking",
                            },
                            "unit_amount": price * 100,
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url="http://localhost:3000/secured/success",
                cancel_url="http://localhost:3000/secured/failed",
                billing_address_collection="required",
                payment_intent_data={
                    "metadata": {
                        "user_id": user_id,
                        "slot_id": slot_id,
                    }
                },
            )
            print(checkout_session.url, "url")
            # return redirect(checkout_session.url, code=303)
            return Response({"url": checkout_session.url}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            # return e
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class Webhook(APIView):
    def post(self, request):
        print("arrived")
        event = None
        payload = request.body
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]

        print("webhook")
        print(webhook_secret)
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
            handle_payment(payment_intent)
        elif event.type == "payment_method.attached":
            payment_method = event.data.object
            print("--------payment_method ---------->", payment_method)
        # ... handle other event types
        else:
            print("Unhandled event type {}".format(event.type))
        # return JsonResponse(success=True, safe=False)
        return JsonResponse({"success": True})


def handle_payment(payment_intent):
    print("arrived")
    user_id = payment_intent["metadata"]["user_id"]
    slot_id = payment_intent["metadata"]["slot_id"]
    print(user_id, "id of user")
    print(slot_id, "id of slot")
    payment_id = payment_intent["id"]
    amount_paid = payment_intent["amount"] / 100
    print(amount_paid, "amount_paid")
    status = payment_intent["status"]
    print(status, "stat")
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        pass
    try:
        slot = Available.objects.get(id=slot_id)
    except Available.DoesNotExist:
        pass
    booking = Booking.objects.create(
        user=user,
        slot=slot,
        date=slot.date,
        payment_id=payment_id,
        amount_paid=amount_paid,
        status="suceessfull",
    )
    booking.save()
    print("booking instance created", booking.id)
    print("booking instance created", booking.created_at)


@api_view(["GET"])
def bookings(request):
    user_id = request.query_params.get("userId")
    print(user_id, "why")
    try:
        bookings = Booking.objects.filter(user=user_id).order_by("-id").first()
        print(bookings.slot)
        print(bookings.slot.associate.name, "name of associate")
        associate_name = bookings.slot.associate.name
        booking_serializer = BookingSerializer(bookings)
        associate_serializer = AssociateSerializer(bookings.slot.associate)

        booking_data = booking_serializer.data
        # Add the name of the associate to the booking data
        booking_data["associate_name"] = associate_serializer.data["name"]

        return Response(
            {
                "booking": booking_data,
            },
            status=status.HTTP_200_OK,
        )
    except Booking.DoesNotExist:
        return Response(
            {"message": "No bookings found for the user"},
            status=status.HTTP_404_NOT_FOUND,
        )
