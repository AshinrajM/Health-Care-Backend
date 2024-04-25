from django.urls import path
from .views import *

urlpatterns = [
    path("slot/", AvailableView.as_view(), name="available"),
    path("checkout", StripeCheckout.as_view(), name="stripe-checkout"),
    path("webhook-test/", Webhook.as_view()),
    path("latest-booking", booking_details, name="latest_booking"),
    path("bookings", bookings, name="bookings"),
]
