# Django Third-party modules
from rest_framework import serializers


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
    errors = serializers.DictField(
        child=serializers.ListField(child=serializers.CharField()),
        required=False,
    )
