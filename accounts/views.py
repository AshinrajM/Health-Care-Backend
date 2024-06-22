import stripe
import pyotp
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.decorators import api_view, permission_classes
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from .models import *
from booking.models import *
from booking.serializers import *
from django.db.models import Q, Avg
from django.db import transaction
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.hashers import check_password
from utils.mail_utils import send_notification_email
from booking.tasks import send_email


class UsersManageView(APIView):

    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [AllowAny]

    def get(self, request, pk=None):
        users = User.objects.filter(
            Q(is_associate=False) & Q(is_superuser=False) & Q(is_staff=False)
        )
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

    permission_classes = [AllowAny]

    def get(self, request):
        associates = Associate.objects.all()
        serializer = AssociateSerializer(associates, many=True)
        return Response(serializer.data)

    def patch(self, request):
        print("patch---------------------------------------")

        try:
            associate_id = request.data.get("associateId")
            print("arrived")
            associate = Associate.objects.get(id=associate_id)
            user = User.objects.get(associate=associate)

            if not associate.is_active:
                associate.is_active = True
                associate.save()
                user.is_active = True
                user.save()

                subject = "HealthCare: Your Account has been UnBlocked"
                message = "Your account has been Unblocked, You can begin your work from today"
                send_email(subject, message, user.email)
                return Response(
                    {"success": "Associate deactivated successfully."},
                    status=status.HTTP_200_OK,
                )

            slots = Available.objects.filter(associate=associate)
            slots.update(status="associate_blocked")

            bookings = Booking.objects.filter(
                slot__associate=associate, status="confirmed"
            )

            if not bookings.exists():
                # If no bookings exist, deactivate the associate and user
                associate.is_active = False
                associate.save()
                user.is_active = False
                user.save()

                subject = "HealthCare: Your Account has been Blocked"
                message = (
                    "Your account has been blocked due to low performance ratings. "
                    "Please contact support for further assistance."
                )
                send_email(subject, message, user.email)
                print("completed with no bookings")
                return Response(
                    {"success": "Associate deactivated successfully."},
                    status=status.HTTP_200_OK,
                )

            with transaction.atomic():
                for booking in bookings:
                    try:
                        refund = stripe.Refund.create(payment_intent=booking.payment_id)
                        if refund.status == "succeeded":
                            booking.status = "cancelled_by_admin"
                            booking.save()
                            booking.slot.status = "associate_blocked"
                            booking.slot.save()

                            subject = "HealthCare , Your Booking got cancelled"
                            message = f"Booking cancelled on {booking.date} and because of the immediate problem faced by the associate and refund procedure initiated, there will be deductions in this. Apologies from our side."
                            recipient = booking.user.email
                            send_email(subject, message, recipient)

                        else:
                            # Handle refund failure
                            return Response(
                                {"error": "Failed to refund the payment."},
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                    except stripe.error.StripeError as e:
                        # Handle Stripe errors
                        return Response(
                            {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
                        )
                    except Exception as e:
                        # Handle other exceptions
                        return Response(
                            {"error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        )
            associate.is_active = False
            associate.save()
            user.is_active = False
            user.save()
            subject = "HealthCare , Your  account has been got blocked"
            message = f"Your account has been blocked ,the ratings for your performance is very low so your account has temperorily blocked"
            recipient = user.email
            send_email(subject, message, recipient)
            return Response(
                {"success": "Bookings cancelled and refunded successfully."},
                status=status.HTTP_200_OK,
            )

        except Associate.DoesNotExist:
            return Response(
                {"error": "Associate not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def update_associate_fee_per_hour(request):
    fee_per_hour = request.data.get("salary")
    associate_id = request.data.get("associateId")
    try:
        associate = Associate.objects.get(id=associate_id)
        associate.fee_per_hour = fee_per_hour
        associate.save()
        serializer = AssociateSerializer(associate)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Associate.DoesNotExist:
        return Response(
            {"error": "Associate not found."}, status=status.HTTP_404_NOT_FOUND
        )


class RegisterView(APIView):

    permission_classes = [AllowAny]

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
        recipient_list = [email]

        send_email(subject, message, recipient_list)

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

    permission_classes = [AllowAny]

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

    permission_classes = [IsAdminUser]

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
        send_email(subject, message, to_mail)

        return Response(associate_serializer.data, status=status.HTTP_201_CREATED)


class GoogleSignUp(CreateAPIView):

    permission_classes = [AllowAny]

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserLoginView(APIView):

    permission_classes = [AllowAny]

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

    permission_classes = [AllowAny]

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

            send_email(subject, message, recipient_list)

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

    permission_classes = [AllowAny]

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


# to get the latest associate-user data
@api_view(["GET"])
@permission_classes([IsAuthenticated])
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
                Q(slot__associate__user=user) & Q(status="completed")
            ).count()

            completed_bookings = Booking.objects.filter(
                Q(slot__associate__user=user) & Q(status="completed")
            )
            average_rating = completed_bookings.aggregate(
                average_rating=Avg("rating__rating_value")
            )

        combined_data = {
            "user": serializer.data,
            "available_slots": available_serializer.data,
            "count": bookings_count,
            "average_rating": average_rating,
        }
        return Response(combined_data, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response(
            {"error": "user doesnt exist"}, status=status.HTTP_404_NOT_FOUND
        )


# @api_view(["GET"])
# def get_associate(request):
#     user_id = request.query_params.get("userId")
#     try:
#         user = User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         return Response({"error": "User not found."}, status=404)

#     try:
#         associate = Associate.objects.get(user=user)
#     except Associate.DoesNotExist:
#         return Response({"error": "Associate not found."}, status=404)

#     serializer = AssociateUserDataSerializer(associate)
#     return Response(serializer.data, status=status.HTTP_200_OK)
