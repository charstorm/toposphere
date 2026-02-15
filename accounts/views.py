from typing import Any

from rest_framework import status
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


class RegisterView(APIView):  # type: ignore[misc]
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):  # type: ignore[misc]
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):  # type: ignore[misc]
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            user = request.user
            validated_data: dict[str, Any] = serializer.validated_data
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

    def get(self, request: Request) -> Response:
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request: Request) -> Response:
        serializer = ProfileSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request: Request) -> Response:
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteAccountView(APIView):  # type: ignore[misc]
    permission_classes = [IsAuthenticated]

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


# accounts/views.py
