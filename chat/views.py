from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .models import *
from .serializer import *
from django.contrib.auth.decorators import login_required
from django.db.models import Q


# Create your views here.


@api_view(["GET"])
def identify(request):
    role = request.query_params.get("role")
    id = request.query_params.get("userId")
    print(role, "see role")
    print(id, "id from params")
    if role == "user":
        try:
            user = User.objects.get(id=id)
            print(user.email, "user got")
            receiver = user.email.split("@")[0]
            print(receiver, "name of the opposite person")
        except Associate.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class GetMessage(APIView):
    def get(self, request):
        sender_id = request.query_params.get("sender")
        receiver_id = request.query_params.get("receiver")

        print(sender_id, receiver_id, "show re")

        if not sender_id or not receiver_id:
            return Response(
                {"error": "sender and receiver parameters are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        query_set = Chat.objects.filter(
            Q(author=sender_id) | Q(receiver=sender_id),
            Q(author=receiver_id) | Q(receiver=receiver_id),
        ).order_by("created")

        serializer = ChatSerializer(query_set, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
