from django.urls import path
from .views import *

urlpatterns = [
    path("register", RegisterView.as_view(), name="register"),
    path("verify", VerifyView.as_view(), name="verify"),
    path("login", UserLoginView.as_view(), name="login"),
    path(
        "register-associate", RegisterAssociateView.as_view(), name="register_associate"
    ),
    path("userslist", UsersManageView.as_view(), name="users-list"),
    path("associatelist", AssociateListView.as_view(), name="associate-list"),
    path(
        "reset-password-validate",
        UserResetPasswordView.as_view(),
        name="reset_password",
    ),
    path("reset-verify-otp", OtpVerifyView.as_view(), name="reset_verify_otp"),
]
