from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password:
            instance.set_password(password)
            instance.save()
            return instance


class UserLoginSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        print(email)
        print(password)
        print("-=--------------------------------------------")

        if email and password:
            user = User.objects.filter(email=email).first()
            if user:
                return data
            raise serializers.ValidationError("invalid user credentials")
        raise serializers.ValidationError("Both fields are required")

