from rest_framework import serializers
from .models import *
from accounts.serializers import AssociateSerializer


class AvailableSerializer(serializers.ModelSerializer):
    associate = AssociateSerializer()

    class Meta:
        model = Available
        fields = "__all__"


