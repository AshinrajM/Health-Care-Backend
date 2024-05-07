from django.urls import path
from .views import *

urlpatterns = [
    path("available-list/", Available_List, name="available_list"),
    path("slot/", AvailableView.as_view(), name="available"),
    path("checkout", StripeCheckout.as_view(), name="stripe-checkout"),
    path("webhook-test/", Webhook.as_view()),
    path("latest-booking", booking_details, name="latest_booking"),
    path("bookings", bookings, name="bookings"),
    path("associate-booking", Booking_view.as_view(), name="associate_booking"),
    path("booking-list/", booking_list, name="booking_list"),
]
