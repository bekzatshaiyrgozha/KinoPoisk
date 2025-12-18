# Django Third-party modules
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample


class BaseResponseSerializer(serializers.Serializer):
    """Base serializer for all API responses."""

    success = serializers.BooleanField()
    message = serializers.CharField(required=False)


class SuccessResponseSerializer(BaseResponseSerializer):
    """Serializer for successful API responses."""

    data = serializers.JSONField(required=False)


class ErrorResponseSerializer(BaseResponseSerializer):
    """Serializer for error API responses."""

    success = serializers.BooleanField(default=False)
    message = serializers.CharField(default="Bad request")
    errors = serializers.DictField(
        child=serializers.ListField(child=serializers.CharField()),
        required=False,
    )


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "401 Unauthorized",
            value={
                "success": False,
                "message": "Authentication credentials were not provided.",
                "errors": {},
            },
            response_only=True,
        )
    ]
)
class UnauthorizedResponseSerializer(serializers.Serializer):
    """401 Unauthorized response"""

    success = serializers.BooleanField(default=False)
    message = serializers.CharField(
        default="Authentication credentials were not provided."
    )


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "403Forbidden",
            value={
                "success": False,
                "message": "You do not have permission to perform this action.",
                "errors": {},
            },
            response_only=True,
        )
    ]
)
class ForbiddenResponseSerializer(serializers.Serializer):
    """403 Forbidden response"""

    success = serializers.BooleanField(default=False)
    message = serializers.CharField(
        default="You do not have permission to perform this action."
    )


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "404 Not Found",
            value={
                "success": False,
                "message": "Not found",
            },
            response_only=True,
        )
    ]
)
class NotFoundResponseSerializer(serializers.Serializer):
    """404 Not Found response"""

    success = serializers.BooleanField(default=False)
    message = serializers.CharField(default="The requested resource was not found.")


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "405 Method Not Allowed",
            value={"success": False, "message": "Method not allowed.", "errors": {}},
            response_only=True,
        )
    ]
)
class MethodNotAllowedResponseSerializer(serializers.Serializer):
    """405 Method Not Allowed response"""

    success = serializers.BooleanField(default=False)
    message = serializers.CharField(default="Method not allowed.")
