from rest_framework.views import APIView
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from .models import *
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings


class UsersListView(APIView):
    def get(self, request, pk=None):
        users = User.objects.filter(is_associate=False)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class AssociateListView(APIView):
    def get(self, request):
        associates = Associate.objects.all()
        serializer = AssociateSerializer(associates, many=True)
        return Response(serializer.data)
        # users = User.objects.filter(is_associate=True)
        # serializer = UserSerializer(users, many=True)
        # return Response(serializer.data)


class RegisterView(APIView):
    def post(self, request):

        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RegisterAssociateView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        # want to send a mail to the associate this password as a content for his firt login

        serializer = AssociateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        print("---------user creation success", user.email)
        print("---------user creation success")

        formData = request.data.copy()
        formData["user"] = user.id

        print("------------user id addded to form data ")

        associate_serializer = AssociateSerializer(data=formData)
        associate_serializer.is_valid(raise_exception=True)
        associate_serializer.save()

        print("associate creation success")

        subject = "Welcome to HealthCare, This is a confidential mail with password for your associate login"
        message = password
        from_mail = settings.EMAIL_HOST_USER
        to_mail = [email]
        send_mail(subject, message, from_mail, to_mail)

        return Response(associate_serializer.data, status=status.HTTP_201_CREATED)

    def patch(APIView):
        pass


class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        email = serializer.data.get("email")
        password = serializer.data.get("password")

        user = authenticate(email=email, password=password)

        if user:
            login(request, user)

            refresh = RefreshToken.for_user(user)

            role = (
                "associate"
                if user.is_associate
                else ("superuser" if user.is_superuser else "user")
            )

            refresh["role"] = role
            refresh["user"] = user.email

            user_details = UserSerializer(user)
            user_data = user_details.data
  
            data = {}
            data["role"] = role
            data["refresh"] = str(refresh)
            data["access"] = str(refresh.access_token)
            data["user"] = user_data

            return Response(data, status=status.HTTP_200_OK)
        return Response(
            {"messages": "Invalid user credentials"},
            status=status.HTTP_404_NOT_FOUND,
        )
