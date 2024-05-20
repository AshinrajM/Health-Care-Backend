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
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY
webhook_secret = settings.STRIPE_WEBHOOK_SECRET


@api_view(["GET"])
# user side
def Available_List(request):
    availabilities = Available.objects.exclude(booking__isnull=False)
    serializer = AvailableSerializer(availabilities, many=True)
    serializer = AvailableSerializer(availabilities, many=True)
    for data in serializer.data:
        associate_id = data[
            "associate"
        ]  # Assuming associate_id is present in the serializer data
        associate_instance = Associate.objects.get(id=associate_id)
        associate_serializer = AssociateSerializer(associate_instance)
        data["associate"] = associate_serializer.data
        print(serializer.data, "check else section")
    return Response(serializer.data, status=status.HTTP_200_OK)


class AvailableView(APIView):
    # associate - schedules on associate side
    def get(self, request):
        associate_id = request.query_params.get("associate_id", None)
        print(associate_id, "id received")
        if associate_id:
            availabilities = Available.objects.filter(associate=associate_id)
        # else:
        #     # this query will exclude instances which are also in booking
        #     print("else in slot check")
        #     availabilities = Available.objects.exclude(booking__isnull=False)
        #     print(availabilities, "show datas")
        serializer = AvailableSerializer(availabilities, many=True)
        for data in serializer.data:
            associate_id = data[
                "associate"
            ]  # Assuming associate_id is present in the serializer data
            associate_instance = Associate.objects.get(id=associate_id)
            associate_serializer = AssociateSerializer(associate_instance)
            data["associate"] = associate_serializer.data
            print(serializer.data, "check else section")
        return Response(serializer.data, status=status.HTTP_200_OK)

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
        shift = request.data.get("shift")
        print(shift, "in stripe check")

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
                    "metadata": {"user_id": user_id, "slot_id": slot_id, "shift": shift}
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
    print("arrived in booking creation")
    user_id = payment_intent["metadata"]["user_id"]
    slot_id = payment_intent["metadata"]["slot_id"]
    shift = payment_intent["metadata"]["shift"]
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
        status="confirmed",
    )
    booking.save()
    print("booking instance created", booking.id)
    print("booking instance created", booking.created_at)


@api_view(["GET"])
def booking_details(request):
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


# booking history - user
@api_view(["GET"])
def bookings(request):
    user_id = request.query_params.get("userId")
    print(user_id, "why")

    # By default, if include_associate query parameter is not provided or set to true,
    # the slot data will be included
    include_associate = (
        request.query_params.get("include_associate", "true").lower() == "true"
    )

    try:
        bookings = Booking.objects.filter(user=user_id)
        booking_serializer = BookingSerializer(
            bookings, many=True, context={"include_associate": include_associate}
        )
        booking_data = booking_serializer.data
        return Response({"booking": booking_data}, status=status.HTTP_200_OK)
    except Booking.DoesNotExist:
        return Response(
            {"message": "No bookings found for the user"},
            status=status.HTTP_404_NOT_FOUND,
        )


# associate
class Booking_view(APIView):
    def get(self, request):
        associate_id = request.query_params.get("associateId")
        print(associate_id, "working")
        if associate_id:
            try:
                bookings = Booking.objects.filter(
                    slot__associate_id=associate_id
                ).select_related("user")
                # print("bookinfs", bookings)
                serializer = AssociateBookings(bookings, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Booking.DoesNotExist:
                return Response(
                    {"message": "No bookings found for the Associate"},
                    status=status.HTTP_404_NOT_FOUND,
                )

    def patch(self, request):
        bookingId = request.data.get("bookingId")
        updated_status = request.data.get("updatedStatus")
        print("update of status", bookingId, ",", updated_status)

        try:
            booking = Booking.objects.get(booking_id=bookingId)
            print(booking.slot.associate.user, "checking associate")
            associateUser = booking.slot.associate.user
            associate_share = booking.amount_paid * Decimal("0.6")
            print(associate_share, "fee ")
            associateUser.wallet += associate_share
            associateUser.save()
            booking.status = updated_status
            booking.save()
            return Response({"message": "updated booking"}, status=status.HTTP_200_OK)
        except Booking.DoesNotExist:
            return Response(
                {"error": "booking doesnt exist"}, status=status.HTTP_404_NOT_FOUND
            )


@api_view(["GET"])
def booking_list(request):
    try:
        bookings = Booking.objects.all().select_related("user", "slot__associate")
        serializer = AssociateBookings(bookings, many=True)
        print("booking list working")
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Booking.DoesNotExist:
        return Response(
            {"message": "No bookings found"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["PATCH"])
def cancel_booking(request):
    booking_id = request.data.get("bookingId")
    user_id = request.data.get("userId")

    print(booking_id,user_id,"received datas")

    try:
        booking = Booking.objects.get(booking_id=booking_id)
        user = User.objects.get(id=user_id)
        booking.status = "cancelled"
        booking.save()
        cancel_charge = booking.amount_paid * Decimal("0.1")
        refund_amount = booking.amount_paid - cancel_charge
        user.wallet += refund_amount
        user.save()
        return Response({'message':'booking cancelled successfully'},status=status.HTTP_200_OK)
    except (Booking.DoesNotExist, User.DoesNotExist) as e:
        return Response({"error": "Booking or User not found"}, status=status.HTTP_404_NOT_FOUND)

        
        # if isinstance(e, Booking.DoesNotExist):
        # else:
        #     return JsonResponse(
        #         {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
        #     )
