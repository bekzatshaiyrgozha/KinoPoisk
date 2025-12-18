from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Error Example",
            summary="Standard error response",
            description="Example of a standard error response",
            value={"detail": "Not found."},
        )
    ]
)
class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error responses (400, 404, etc.)"""

    detail = serializers.CharField(help_text="Error message")


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Validation Error Example",
            summary="Validation error response",
            description="Example of validation errors",
            value={
                "detail": "Invalid input.",
                "username": ["This field is required."],
                "email": ["Enter a valid email address."],
                "password": ["This password is too common."],
            },
        )
    ]
)
class ValidationErrorResponseSerializer(serializers.Serializer):
    """Serializer for validation error responses (400)"""

    detail = serializers.CharField(required=False, help_text="General error message")
    username = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Username validation errors",
    )
    email = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Email validation errors",
    )
    password = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Password validation errors",
    )


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Success Example",
            summary="Success message",
            description="Example of a success message",
            value={"message": "Operation successful."},
        )
    ]
)
class SuccessMessageSerializer(serializers.Serializer):
    """Serializer for success message responses"""

    message = serializers.CharField(help_text="Success message")


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Auth Response Example",
            summary="Authentication response",
            description="Example of a successful authentication response",
            value={
                "user": {
                    "id": 1,
                    "username": "johndoe",
                    "email": "john@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                },
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "message": "Login successful",
            },
        )
    ]
)
class AuthResponseSerializer(serializers.Serializer):
    """Serializer for authentication responses"""

    user = serializers.DictField(help_text="User information")
    refresh = serializers.CharField(help_text="Refresh token")
    access = serializers.CharField(help_text="Access token")
    message = serializers.CharField(help_text="Response message")
