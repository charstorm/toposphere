import re
from typing import Any

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class CustomPasswordValidator:
    def validate(self, password: str, user: Any = None) -> None:
        if len(password) < 8:
            raise ValidationError(
                _("Password must be at least 8 characters long"),
                code="password_too_short",
            )

        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                _("Password must contain at least 1 uppercase letter"),
                code="password_no_upper",
            )

        if not re.search(r"[a-z]", password):
            raise ValidationError(
                _("Password must contain at least 1 lowercase letter"),
                code="password_no_lower",
            )

        if not re.search(r"\d", password):
            raise ValidationError(
                _("Password must contain at least 1 digit"),
                code="password_no_digit",
            )

    def get_help_text(self) -> str:
        return str(
            _(
                "Your password must be at least 8 characters long, contain at least "
                "1 uppercase letter, 1 lowercase letter, and 1 digit."
            )
        )


# accounts/validators.py
