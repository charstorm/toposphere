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


# accounts/tests.py
