from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.abstracts.models import AbstractBaseModel
from apps.accounts.managers import CustomUserManager


class CustomUser(AbstractUser, AbstractBaseModel):
    """
    Custom User Model
    Fields:
        - email: Unique email address for the user
        - bio: Optional biography of the user
    Methods:
        - __str__: String representation of the user
        - __repr__: Official representation of the user
        - full_name: Returns the full name of the user
        - short_name: Returns the short name of the user
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
