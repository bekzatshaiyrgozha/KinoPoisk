# Django modules
import uuid
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.core.validators import validate_email
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample

User = get_user_model()


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "User Example",
            summary="Example of user data",
            description="Standard user response object",
            value={
                "id": 1,
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "date_joined": "2023-01-01T12:00:00Z",
                "is_active": True,
                "is_staff": False,
            },
        )
    ]
)
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model representation.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "date_joined",
            "is_active",
            "is_staff",
        ]
        read_only_fields = ["id", "date_joined", "is_staff"]
        extra_kwargs = {
            "email": {"help_text": "User's email address (used for login)"},
            "first_name": {"help_text": "User's first name"},
            "last_name": {"help_text": "User's last name"},
            "date_joined": {"help_text": "Date and time when the user registered"},
            "is_active": {
                "help_text": "Designates whether this user should be treated as active"
            },
            "is_staff": {
                "help_text": "Designates whether the user can log into this admin site"
            },
        }


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Registration Example",
            summary="Valid registration data",
            description="Example of data required for user registration",
            value={
                "email": "newuser@example.com",
                "first_name": "New",
                "last_name": "User",
                "password": "strongpassword123",
                "password_confirm": "strongpassword123",
            },
            request_only=True,
        )
    ]
)
class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles creation of new users with password validation.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
        help_text="User password (min 8 characters)",
        label="Password",
    )
    password_confirm = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
        help_text="Confirm password (must match password)",
        label="Password Confirmation",
    )

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
        ]
        extra_kwargs = {
            "email": {"required": True, "help_text": "Valid email address"},
            "first_name": {"help_text": "Optional first name"},
            "last_name": {"help_text": "Optional last name"},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords don't match"}
            )
        email = attrs.get("email")
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"email": "A user with this email already exists."}
            )

        return attrs

    def validate_email(self, value):
        value = value.lower().strip()
        try:
            validate_email(value)
        except:  # noqa: E722
            raise serializers.ValidationError("Enter a valid email address.")
        return value

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        # Generate a unique username since it's required by AbstractUser
        # We use UUID to ensure uniqueness and because the user doesn't care about it
        validated_data["username"] = f"user_{uuid.uuid4().hex[:10]}"
        user = User.objects.create_user(**validated_data)
        return user


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Login Example",
            summary="Valid login credentials",
            description="Example of data required for user login",
            value={
                "email": "user@example.com",
                "password": "mypassword123",
            },
            request_only=True,
        )
    ]
)
class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Authenticates user with email and password.
    """

    email = serializers.EmailField(
        required=True,
        help_text="Registered email address",
        label="Email",
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        help_text="User password",
        label="Password",
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email:
            email = email.lower().strip()
            attrs["email"] = email

        user = authenticate(
            request=self.context.get("request"), email=email, password=password
        )

        if not user:
            raise serializers.ValidationError(
                "Unable to log in with provided credentials."
            )

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        attrs["user"] = user
        return attrs

    def validate_email(self, value):
        """Базовая валидация email"""
        value = value.lower().strip()
        try:
            validate_email(value)
        except:  # noqa: E722
            raise serializers.ValidationError("Enter a valid email address.")
        return value
