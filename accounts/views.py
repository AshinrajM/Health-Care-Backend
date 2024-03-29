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
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.hashers import check_password


class UsersManageView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, pk=None):
        users = User.objects.filter(is_associate=False)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def patch(self, request):
        location = request.data.get("location")
        # print(location, "received location")
        p = request.data.get("profile_picture")
        # print(p, "picture")

        current_password = request.data.get("currentPassword")
        new_password = request.data.get("newPassword")
        print(current_password, new_password, "show received datas")

        # print("arrived patch method")
        user_id = request.data.get("id")
        if not user_id:
            return Response(
                {"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if current_password and new_password:
            print("validation-1")
            if check_password(current_password, user.password):
                print("validation-2")
                user.set_password(new_password)
                user.save()
            else:
                print("didnt changed password")
                return Response(
                    {"error": "Invalid current password."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # print(" sending to serializer")
        serializer = UserSerializer(user, data=request.data, partial=True)
        # print(" received from serializer")

        if serializer.is_valid():
            print("if c::::::::")
            serializer.save()
            # print(serializer.data, "success")
            return Response(serializer.data, status=status.HTTP_200_OK)
        print("else c::::::::::")
        # print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

    def patch(self, request):
        print("aarrived patch")
        user_id = request.data.get("userId")
        print(request.data, "SAMPLe")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        user.is_active = not user.is_active
        user.save()

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegisterAssociateView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        # want to send a mail to the associate this password as a content for his first login

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

            if role == "associate":
                associate = Associate.objects.get(user=user)
                associate_data = AssociateSerializer(associate).data
                data["associate"] = associate_data
            print(data)
            return Response(data, status=status.HTTP_200_OK)

        # If authentication fails, check for specific reasons (email, password, or both)
        errors = {}
        if not errors:
            errors["messages"] = "Invalid email or password"

        return Response(
            errors,
            status=status.HTTP_401_UNAUTHORIZED,
        )
