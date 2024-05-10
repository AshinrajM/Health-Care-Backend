from django.urls import path, include
from .views import *

urlpatterns = [
    path("identify", identify, name="Checking"),
]
