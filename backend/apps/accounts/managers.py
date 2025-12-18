# Python modules
from typing import Any, TYPE_CHECKING

# Django modules
from django.contrib.auth.models import BaseUserManager

if TYPE_CHECKING:
    from apps.accounts.models import CustomUser


class CustomUserManager(BaseUserManager):
    """
    Custom user manager where email is the unique identifier
    for authentication instead of usernames.
    """

    def create_user(
        self, email: str, password: str, **extra_fields: Any
    ) -> "CustomUser":
        if not email:
            raise ValueError("Email address is required")

        email = self.normalize_email(email)
        if "username" not in extra_fields:
            extra_fields["username"] = email.split("@")[0]

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, password: str, **extra_fields: Any
    ) -> "CustomUser":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")
        return self.create_user(email, password, **extra_fields)
