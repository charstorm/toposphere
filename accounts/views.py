from typing import Any, cast

from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    ChangePasswordSerializer,
    DeleteAccountSerializer,
    LoginSerializer,
    ProfileSerializer,
    RegisterSerializer,
)


class MessageResponseSerializer(serializers.Serializer):  # type: ignore[misc]
    message = serializers.CharField()


class RegisterView(APIView):  # type: ignore[misc]
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: RegisterSerializer,
            400: serializers.ValidationError,
        },
        description="Register a new user account.",
    )
    def post(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):  # type: ignore[misc]
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: LoginSerializer,
            400: serializers.ValidationError,
        },
        description="Authenticate user and return auth token.",
    )
    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):  # type: ignore[misc]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            200: MessageResponseSerializer,
            400: serializers.ValidationError,
        },
        description="Change the authenticated user's password.",
    )
    def post(self, request: Request) -> Response:
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            user = request.user
            validated_data = cast(dict[str, Any], serializer.validated_data)
            new_password: str = validated_data["new_password"]
            if new_password:
                user.set_password(new_password)
                user.save()
            return Response(
                {"message": "Password changed successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):  # type: ignore[misc]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: ProfileSerializer},
        description="Get the authenticated user's profile.",
    )
    def get(self, request: Request) -> Response:
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        request=ProfileSerializer,
        responses={
            200: ProfileSerializer,
            400: serializers.ValidationError,
        },
        description="Update the authenticated user's profile (full update).",
    )
    def put(self, request: Request) -> Response:
        serializer = ProfileSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=ProfileSerializer,
        responses={
            200: ProfileSerializer,
            400: serializers.ValidationError,
        },
        description="Partially update the authenticated user's profile.",
    )
    def patch(self, request: Request) -> Response:
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteAccountView(APIView):  # type: ignore[misc]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=DeleteAccountSerializer,
        responses={
            200: MessageResponseSerializer,
            400: serializers.ValidationError,
        },
        description="Delete the authenticated user's account.",
    )
    def post(self, request: Request) -> Response:
        serializer = DeleteAccountSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            user = request.user
            user.delete()
            return Response(
                {"message": "Account deleted successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
