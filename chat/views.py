from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from accounts.models import User
from django.contrib.auth.decorators import login_required


# Create your views here.
 
# @login_required
@api_view(["GET"])
def check(request):
    # user_id = request.user.id
    # print("id", user_id)
    # # user = User.objects.get(id=user_id)
    # # print("user name", user.email)
    return Response({"message": "checking chat app"}, status=status.HTTP_200_OK)
