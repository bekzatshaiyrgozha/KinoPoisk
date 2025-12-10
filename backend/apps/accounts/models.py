from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.abstracts.models import AbstractBaseModel
from apps.accounts.managers import CustomUserManager


class CustomUser(AbstractUser, AbstractBaseModel):
    """
    Custom User Model
    """

    email = models.EmailField(
        unique=True,
        verbose_name="Email Address",
        help_text="Required. User email address for login",
    )
    bio = models.TextField(blank=True, verbose_name="Bio")

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]
        db_table = "custom_users"

    def __str__(self):
        return self.email

    def __repr__(self):
        return f"<CustomUser {self.id}:{self.email}>"

    @property
    def full_name(self) -> str:
        return self.get_full_name()

    @property
    def short_name(self) -> str:
        return self.get_short_name()
