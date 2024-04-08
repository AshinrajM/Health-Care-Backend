from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from .serializers import *
from rest_framework import status
from rest_framework.response import Response

# Create your views here.


class AvailableView(APIView):
    def get(self, request):
        availabilities = Available.objects.all()
        serializer = AvailableSerializer(availabilities, many=True)
        for data in serializer.data:
            associate_id = data["associate"]  # Assuming associate_id is present in the serializer data
            associate_instance = Associate.objects.get(id=associate_id)
            associate_serializer = AssociateSerializer(associate_instance)
            data["associate"] = associate_serializer.data
        return Response(serializer.data)

    def post(self, request):
        serializer = AvailableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
