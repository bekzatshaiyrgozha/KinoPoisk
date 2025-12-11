from rest_framework import serializers


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error responses (400, 404, etc.)"""

    detail = serializers.CharField(help_text="Error message")


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


class SuccessMessageSerializer(serializers.Serializer):
    """Serializer for success message responses"""

    message = serializers.CharField(help_text="Success message")


class AuthResponseSerializer(serializers.Serializer):
    """Serializer for authentication responses"""

    user = serializers.DictField(help_text="User information")
    refresh = serializers.CharField(help_text="Refresh token")
    access = serializers.CharField(help_text="Access token")
    message = serializers.CharField(help_text="Response message")
