from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import *
from rest_framework import status
from rest_framework.response import Response

# Create your views here.


class AvailableView(APIView):

    def post(self, request):
        try:
            print("Data received:", request.data)
            associate_id = request.data.get("associate_id")
            print(associate_id, "auuuuuuuuuuu")
            associate = Associate.objects.get(id=associate_id)
            print("assoooo", associate.name)

            data = request.data.copy()
            if "associate_id" in data:
                del data["associate_id"]

            data["associate"] = associate.id

            serializer = AvailableSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Associate.DoesNotExist:
            raise NotFound("Associate matching query does not exist.")
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get(self, request):
        list = Available.objects.all()
        serializer = AvailableSerializer(Available, many=True)
        return Response(serializer.data)
