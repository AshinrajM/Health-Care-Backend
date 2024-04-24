from rest_framework import serializers
from .models import *
from accounts.serializers import AssociateSerializer


class AvailableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Available
        fields = ["id", "associate", "date", "is_morning", "is_noon"]


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"
