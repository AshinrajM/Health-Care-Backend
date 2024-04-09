from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from .serializers import *
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q

# Create your views here.


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


# class
