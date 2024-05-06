from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
# Create your views here.


@api_view(["POST"])
def check(request):
    return Response({"message": "checking chat app"}, status=status.HTTP_200_OK)
