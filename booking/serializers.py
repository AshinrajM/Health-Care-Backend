from rest_framework import serializers
from .models import *
from accounts.serializers import AssociateSerializer


class AvailableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Available
        fields = ["id", "associate", "date", "is_morning", "is_noon"]


class BookingSerializer(serializers.ModelSerializer):
    associate = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = "__all__"

    def get_associate(self, obj):
        if self.context.get("include_associate", True):
            return AssociateSerializer(obj.slot.associate).data
        return None


# Serializer Method Fields in Django DRF provide a dynamic way to customize your API responses. Instead of static values, these fields allow you to define methods that manipulate the data before it's serialized.
