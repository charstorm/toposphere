from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

User = get_user_model()


class RegistrationTests(APITestCase):  # type: ignore[misc]
    def setUp(self) -> None:
        self.url = "/api/auth/register/"
        self.valid_data = {
            "email": "test@example.com",
            "password": "TestPass123",
            "first_name": "Test",
            "last_name": "User",
        }

    def test_registration_success(self) -> None:
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(response.data["email"], self.valid_data["email"])
        self.assertEqual(response.data["first_name"], self.valid_data["first_name"])
        self.assertEqual(response.data["last_name"], self.valid_data["last_name"])
        self.assertIn("token", response.data)
        self.assertTrue(User.objects.filter(email=self.valid_data["email"]).exists())

    def test_registration_duplicate_email(self) -> None:
        User.objects.create_user(email=self.valid_data["email"], password="OtherPass123")
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_registration_weak_password(self) -> None:
        data = self.valid_data.copy()
        data["password"] = "weak"
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_registration_missing_email(self) -> None:
        data = self.valid_data.copy()
        del data["email"]
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_registration_missing_password(self) -> None:
        data = self.valid_data.copy()
        del data["password"]
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_registration_optional_fields(self) -> None:
        data = {"email": "minimal@example.com", "password": "TestPass123"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["first_name"], "")
        self.assertEqual(response.data["last_name"], "")


class LoginTests(APITestCase):  # type: ignore[misc]
    def setUp(self) -> None:
        self.url = "/api/auth/login/"
        self.email = "test@example.com"
        self.password = "TestPass123"
        self.user = User.objects.create_user(email=self.email, password=self.password)
        Token.objects.create(user=self.user)

    def test_login_success(self) -> None:
        response = self.client.post(
            self.url, {"email": self.email, "password": self.password}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["email"], self.email)
        self.assertEqual(response.data["id"], self.user.id)

    def test_login_invalid_password(self) -> None:
        response = self.client.post(
            self.url, {"email": self.email, "password": "wrongpass"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_login_nonexistent_user(self) -> None:
        response = self.client.post(
            self.url,
            {"email": "nonexistent@example.com", "password": "SomePass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_login_missing_email(self) -> None:
        response = self.client.post(self.url, {"password": self.password}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_login_missing_password(self) -> None:
        response = self.client.post(self.url, {"email": self.email}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)


class ChangePasswordTests(APITestCase):  # type: ignore[misc]
    def setUp(self) -> None:
        self.url = "/api/auth/change-password/"
        self.email = "test@example.com"
        self.old_password = "OldPass123"
        self.user = User.objects.create_user(email=self.email, password=self.old_password)
        self.token = Token.objects.create(user=self.user)

    def test_change_password_success(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        data = {
            "old_password": self.old_password,
            "new_password": "NewPass456",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Password changed successfully.")

        # Verify old password no longer works
        login_url = "/api/auth/login/"
        login_response = self.client.post(
            login_url,
            {"email": self.email, "password": self.old_password},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify new password works
        login_response = self.client.post(
            login_url,
            {"email": self.email, "password": "NewPass456"},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

    def test_change_password_wrong_old_password(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        data = {
            "old_password": "WrongPass123",
            "new_password": "NewPass456",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("old_password", response.data)

    def test_change_password_weak_new_password(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        data = {
            "old_password": self.old_password,
            "new_password": "weak",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)

    def test_change_password_unauthorized(self) -> None:
        data = {
            "old_password": self.old_password,
            "new_password": "NewPass456",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileTests(APITestCase):  # type: ignore[misc]
    def setUp(self) -> None:
        self.url = "/api/auth/profile/"
        self.email = "test@example.com"
        self.password = "TestPass123"
        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
            first_name="Test",
            last_name="User",
        )
        self.token = Token.objects.create(user=self.user)

    def test_get_profile_success(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.email)
        self.assertEqual(response.data["first_name"], "Test")
        self.assertEqual(response.data["last_name"], "User")
        self.assertIn("date_joined", response.data)

    def test_get_profile_unauthorized(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile_put_success(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        data = {"first_name": "Updated", "last_name": "Name"}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Updated")
        self.assertEqual(response.data["last_name"], "Name")
        self.assertEqual(response.data["email"], self.email)

    def test_update_profile_patch_success(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        data = {"first_name": "OnlyFirstName"}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "OnlyFirstName")
        self.assertEqual(response.data["last_name"], "User")

    def test_update_profile_unauthorized(self) -> None:
        data = {"first_name": "Updated"}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DeleteAccountTests(APITestCase):  # type: ignore[misc]
    def setUp(self) -> None:
        self.url = "/api/auth/delete-account/"
        self.email = "test@example.com"
        self.password = "TestPass123"
        self.user = User.objects.create_user(email=self.email, password=self.password)
        self.token = Token.objects.create(user=self.user)

    def test_delete_account_success(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        data = {"password": self.password}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Account deleted successfully.")
        self.assertFalse(User.objects.filter(email=self.email).exists())

    def test_delete_account_wrong_password(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        data = {"password": "WrongPass123"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertTrue(User.objects.filter(email=self.email).exists())

    def test_delete_account_missing_password(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        data: dict[str, Any] = {}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_delete_account_unauthorized(self) -> None:
        data = {"password": self.password}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(User.objects.filter(email=self.email).exists())


# accounts/tests.py
