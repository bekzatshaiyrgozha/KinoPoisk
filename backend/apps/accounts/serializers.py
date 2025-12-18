from django.contrib.auth import get_user_model
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample

User = get_user_model()


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="User example",
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
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "date_joined",
            "is_active",
            "is_staff",
        )
        read_only_fields = ("id", "date_joined", "is_staff")
