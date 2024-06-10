from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.decorators import api_view
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from .models import *
from booking.models import *
from booking.serializers import *
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.hashers import check_password
from utils.mail_utils import send_notification_email
import pyotp


class UsersManageView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, pk=None):
        users = User.objects.filter(is_associate=False)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def patch(self, request):
        location = request.data.get("location")
        p = request.data.get("profile_picture")

        current_password = request.data.get("currentPassword")
        new_password = request.data.get("newPassword")
        print(new_password, "new")
        print(current_password, "current")

        user_id = request.data.get("id")
        if not user_id:
            return Response(
                {"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(id=user_id)
            print("user", user.email)
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
                return Response(status=status.HTTP_200_OK)
            else:
                print("didnt changed password")
                return Response(
                    {"message": "Invalid current password."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            print("if c::::::::")
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        print("else c::::::::::")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssociateListView(APIView):

    def get(self, request):
        associates = Associate.objects.all()
        serializer = AssociateSerializer(associates, many=True)
        return Response(serializer.data)


class RegisterView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        print(email, password, "arrived")
        user = User.objects.filter(email=email)
        if user:
            print("user exists")
            return Response(
                {"message": "Email is already registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp = pyotp.TOTP(pyotp.random_base32()).now()

        print(otp, "otp")

        subject = "Welcome to HealthCare, This is the otp for your verification"
        message = f"Hello!\n\nThank you for signing up with HealthCare. Your OTP for account verification   is: {otp}\n\nPlease use this OTP to complete your registration.\n\nIf you did not sign up for a HealthCare account, please ignore this email.\n\nBest regards,\nThe HealthCare Team"
        # from_mail = settings.EMAIL_HOST_USER
        recipient_list = [email]

        # send_mail(subject, message, from_mail, recipient_list)
        send_notification_email(subject, message, recipient_list)

        temp_id = f"{email}_{otp}"
        temp = Temp(temp_id=temp_id, email=email, password=password, otp=otp)
        temp.save()

        return Response({"temp_id": temp_id}, status=status.HTTP_200_OK)

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


class VerifyView(APIView):
    def post(self, request):
        otp = request.data.get("otp")
        temp_id = request.data.get("temp_id")

        try:
            temp_registration = Temp.objects.get(temp_id=temp_id)
            stored = temp_registration.otp

            print("password", temp_registration.password)

            if otp == stored:

                user = User.objects.create_user(
                    email=temp_registration.email, password=temp_registration.password
                )
                user.save()

                temp_registration.delete()

                return Response({"message": "created"}, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST
                )
        except Temp.DoesNotExist:
            return Response(
                {"message": "Invalid temporary ID"}, status=status.HTTP_404_NOT_FOUND
            )


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
        # from_mail = settings.EMAIL_HOST_USER
        to_mail = [email]
        # send_mail(subject, message, from_mail, to_mail)
        send_notification_email(subject, message, from_mail, to_mail)

        return Response(associate_serializer.data, status=status.HTTP_201_CREATED)


class GoogleSignUp(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserLoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        print(email, password, "user login data")

        user = authenticate(email=email, password=password)
        print(user, "Check User::")
        if user:
            print("user data authentication")
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
                print("checking associate login ")
                associate = Associate.objects.get(user=user)
                associate_data = AssociateSerializer(associate).data
                data["associate"] = associate_data
            print(data)
            return Response(data, status=status.HTTP_200_OK)

        else:
            try:
                print(email, "email")
                user = User.objects.get(email=email)
                print(user, "Check User")
                if user:
                    print(user, "exists")
                    return Response(
                        {"detail": "Check password"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
                else:
                    print("user doesmt exist")
                # If the email exists but the password is incorrect, return a custom message
                return Response(
                    {"detail": "Check password"}, status=status.HTTP_401_UNAUTHORIZED
                )
            except User.DoesNotExist:
                # If the email does not exist, return a generic error message
                return Response(
                    {"detail": "Invalid Email "},
                    status=status.HTTP_401_UNAUTHORIZED,
                )


class UserResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(email=email)
            if user.is_google:
                return Response(
                    {"message": "Try log in using google signin"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = UserSerializer(user)
            otp = pyotp.TOTP(pyotp.random_base32()).now()
            temp_id = f"{email}_{otp}"

            subject = "Welcome to HealthCare, This is the otp for your verification"
            message = f"Hello{email}!\n\nWelcome to HealthCare. To reset your account password, please use the following OTP to verify your identity: {otp}\n\nPlease enter this OTP to complete the password reset process.\n\nIf you did not request a password reset for your HealthCare account, please disregard this email.\n\nBest regards,\nThe HealthCare Team"

            # from_mail = settings.EMAIL_HOST_USER

            recipient_list = [email]
            print(recipient_list, "receiver")

            # send_mail(subject, message, from_mail, recipient_list)
            send_notification_email(subject, message, recipient_list)

            print("mail send ")

            temp_id = f"{email}_{otp}"
            temp = Temp(temp_id=temp_id, email=email, otp=otp)
            temp.save()
            return Response({"temp_id": temp_id}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(
                {"message": "Email does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

    def patch(self, request):
        temp_id = request.data.get("tempId")
        password = request.data.get("password")

        try:
            instance = Temp.objects.get(temp_id=temp_id)
            email = instance.email
            try:
                user = User.objects.get(email=email)
                user.set_password(password)
                user.save()
                return Response(
                    {"message": "Password updated successfully"},
                    status=status.HTTP_200_OK,
                )
            except User.DoesNotExist:
                return Response(
                    {"message": "User not found"}, status=status.HTTP_404_NOT_FOUND
                )
        except Temp.DoesNotExist:
            return Response(
                {"error": "Temp ID not found"}, status=status.HTTP_404_NOT_FOUND
            )


class OtpVerifyView(APIView):
    def post(self, request):
        temp_id = request.data.get("tempId")
        otp = request.data.get("otp")
        print("otp verify")
        try:
            instance = Temp.objects.get(temp_id=temp_id, otp=otp)
            print("otp verified")
            return Response({"message": "Otp verified"}, status=status.HTTP_200_OK)
        except Temp.DoesNotExist:
            return Response(
                {"message": "Otp is not valid"}, status=status.HTTP_404_NOT_FOUND
            )


@api_view(["GET"])
def get_user(request):
    user_id = request.query_params.get("userId")

    try:
        user = User.objects.get(id=user_id)
        serializer = UserSerializer(user)
        if user.is_associate:
            available_slots = Available.objects.filter(
                Q(associate__user=user) & Q(status="active")
            )
            available_serializer = AvailableSerializer(available_slots, many=True)

            bookings_count = Booking.objects.filter(
                Q(slot__associate__user=user) & Q(status="confirmed")
            ).count()

        combined_data = {
            "user": serializer.data,
            "available_slots": available_serializer.data,
            "count": bookings_count,
        }
        return Response(combined_data, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response(
            {"error": "user doesnt exist"}, status=status.HTTP_404_NOT_FOUND
        )
