from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from accounts.models import *
from django.contrib.auth.decorators import login_required


# Create your views here.


@api_view(["GET"])
def identify(request):
    role = request.query_params.get("role")
    id = request.query_params.get("userId")
    print(role, "see role")
    print(id, "id from params")
    if role == "user":
        try:
            user = User.objects.get(id=id)
            print(user.email, "user got")
            receiver = user.email.split("@")[0]
            print(receiver, "name of the opposite person")
        except Associate.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    # return Response(status=status.HTTP_200_OK)
