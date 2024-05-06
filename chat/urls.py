from django.urls import path, include
from .views import *

urlpatterns = [
    path("check", check, name="Checking"),
]
