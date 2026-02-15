from django.urls import path

from .views import (
    ChangePasswordView,
    DeleteAccountView,
    LoginView,
    ProfileView,
    RegisterView,
)

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("auth/profile/", ProfileView.as_view(), name="profile"),
    path("auth/delete-account/", DeleteAccountView.as_view(), name="delete-account"),
]

# accounts/urls.py
