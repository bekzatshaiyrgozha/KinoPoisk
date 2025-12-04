from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator
from apps.abstracts.models import AbstractBaseModel
from apps.accounts.managers import CustomUserManager


class CustomUser(AbstractUser, PermissionsMixin, AbstractBaseModel):
    """
    Custom User Model
    """

    email = models.EmailField(
        unique=True,
        verbose_name="Email Address",
        help_text="Required.User email address for login",
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Username",
        help_text="Required.150 characters or fewer",
    )

    # own information for profile
    first_name = models.CharField(max_length=150, blank=True, verbose_name="First Name")

    last_name = models.CharField(max_length=150, blank=True, verbose_name="Last Name")

    bio = models.TextField(blank=True, verbose_name="Bio")

    is_active = models.BooleanField(
        default=True,
        verbose_name="Active Status",
        help_text="User should be trated as active",
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name="Staff Status",
        help_text="User should be trated as staff",
    )
    objects = CustomUserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]
        db_table = "custom_users"
        indexes = [models.Index(fields=["email"]), models.Index(fields=["username"])]

    def __str__(self):
        """
        return email
        """
        return self.email

    def __repr__(self):
        """
        return email and id
        """
        return f"<CustomUsser {self.id}:{self.email}>"

    @property
    def full_name(self) -> str:
        """
        return full name"""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username

    @property
    def short_name(self) -> str:
        """
        return short name
        """
        return self.first_name or self.username

    def get_full_name(self) -> str:
        return self.full_name

    def get_short_name(self) -> str:
        return self.short_name
