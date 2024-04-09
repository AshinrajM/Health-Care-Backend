from django.urls import path
from .views import *

urlpatterns = [
    path("slot/", AvailableView.as_view(), name="available"),
    # path('available')
]
