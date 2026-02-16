from typing import Any

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def get_tokens_for_user(user: Any) -> dict[str, str]:
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


class RegisterSerializer(serializers.ModelSerializer):  # type: ignore[misc]
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "password", "first_name", "last_name", "access", "refresh"]
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
        return user

    def to_representation(self, instance: Any) -> dict[str, Any]:
        data = super().to_representation(instance)
        tokens = get_tokens_for_user(instance)
        data["access"] = tokens["access"]
        data["refresh"] = tokens["refresh"]
        return data  # type: ignore[no-any-return]


class LoginSerializer(serializers.Serializer):  # type: ignore[misc]
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

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
        tokens = get_tokens_for_user(user)
        return {"user": user, "tokens": tokens}

    def to_representation(self, instance: Any) -> dict[str, Any]:
        user = instance["user"]
        tokens = instance["tokens"]
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "access": tokens["access"],
            "refresh": tokens["refresh"],
        }


class ChangePasswordSerializer(serializers.Serializer):  # type: ignore[misc]
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_new_password(self, value: str) -> str:
        validate_password(value)
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        user = self.context["request"].user
        old_password = attrs.get("old_password")

        if not user.check_password(old_password):
            raise serializers.ValidationError({"old_password": "Current password is incorrect."})

        return attrs


class ProfileSerializer(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "date_joined"]
        read_only_fields = ["id", "email", "date_joined"]


class DeleteAccountSerializer(serializers.Serializer):  # type: ignore[misc]
    password = serializers.CharField(write_only=True, required=True)

    def validate_password(self, value: str) -> str:
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Password is incorrect.")
        return value


# accounts/serializers.py
