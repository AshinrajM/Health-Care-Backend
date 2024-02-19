from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = self.Meta.model(**validated_data)
        if password:
            user.set_password(password)
            user.save()
            return user


class AssociateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Associate
        fields = "__all__"

    def create(self, validated_data):
        user_id = validated_data.pop("user", None)
        print(
            "user id got  msg from associateserial -------1---------------------------"
        )

        print(user_id.id)
        if user_id:
            user = User.objects.get(id=user_id.id)

            associate = Associate.objects.create(user=user, **validated_data)
            print(
                "associate created msg from associateuserserial --------------2--------------------"
            )

            return associate


class AssociateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        validated_data["is_associate"] = True
        password = validated_data.pop("password", None)
        user = self.Meta.model(**validated_data)
        if password:
            user.set_password(password)
            user.save()
            print(
                "user created msg from associateuserserial ----------------------------------"
            )
            return user


class UserLoginSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        print(email)
        print(password)

        if email and password:
            user = User.objects.filter(email=email).first()
            if user:
                return data
            raise serializers.ValidationError("invalid user credentials")
        raise serializers.ValidationError("Both fields are required")
