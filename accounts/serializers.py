from typing import Any

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.authtoken.models import Token

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):  # type: ignore[misc]
    token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "password", "first_name", "last_name", "token"]
        extra_kwargs = {
            "password": {"write_only": True},
            "first_name": {"required": False},
            "last_name": {"required": False},
        }

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    def create(self, validated_data: dict[str, Any]) -> Any:
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data, password=password)
        Token.objects.create(user=user)
        return user

    def to_representation(self, instance: Any) -> dict[str, Any]:
        data = super().to_representation(instance)
        token = Token.objects.get(user=instance)
        data["token"] = token.key
        return data  # type: ignore[no-any-return]


class LoginSerializer(serializers.Serializer):  # type: ignore[misc]
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        attrs["user"] = user
        return attrs

    def create(self, validated_data: dict[str, Any]) -> Any:
        user = validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return token

    def to_representation(self, instance: Any) -> dict[str, Any]:
        user = instance.user
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "token": instance.key,
        }


# accounts/serializers.py
