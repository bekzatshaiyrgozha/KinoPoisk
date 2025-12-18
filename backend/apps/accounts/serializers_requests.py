# Django Third-party modules
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Registration request",
            request_only=True,
            value={
                "email": "newuser@example.com",
                "first_name": "New",
                "last_name": "User",
                "password": "strongpassword123",
                "password_confirm": "strongpassword123",
            },
        )
    ]
)
class RegistrationRequestSerializer(serializers.Serializer):
    """Serializer for user registration requests."""

    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Login request",
            request_only=True,
            value={
                "email": "user@example.com",
                "password": "mypassword123",
            },
        )
    ]
)
class LoginRequestSerializer(serializers.Serializer):
    """Serializer for user login requests."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
