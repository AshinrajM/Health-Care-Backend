from rest_framework import serializers
from .models import *
from accounts.serializers import AssociateSerializer


class AvailableSerializer(serializers.ModelSerializer):

    # associate_details = AssociateSerializer(source="associate", read_only=True)
    class Meta:
        model = Available
        fields = ["id", "associate", "date", "is_morning", "is_noon"]
