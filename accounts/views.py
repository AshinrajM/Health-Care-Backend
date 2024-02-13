from rest_framework.views import APIView
from .serializers import UserSerializer, UserLoginSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from .models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404


class RegisterView(APIView):
    def get(self, request, pk=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def delete(self, request, pk):
    #     user = User.objects.filter(pk=pk)
    #     if user:
    #         user.delete()
    #         return Response(
    #             {"message": "User deleted successfully."}, status=status.HTTP_200_OK
    #         )
    #     return Response(
    #         {"msg": "not valid credentials"}, status=status.HTTP_404_NOT_FOUND
    #     )


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

            data = {}
            data["role"] = role
            data["refresh"] = str(refresh)
            data["access"] = str(refresh.access_token)

            return Response(data, status=status.HTTP_200_OK)
        return Response(
            {"messages": "Invalid user credentials"}, status=status.HTTP_404_NOT_FOUND
        )
