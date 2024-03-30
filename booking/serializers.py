from rest_framework import serializers
from .models import *




class AvailableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Available
        fields = "__all__"
