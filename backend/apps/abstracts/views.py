# Django Third-Party modules
from rest_framework import viewsets, serializers
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.status import HTTP_200_OK
from rest_framework.permissions import AllowAny


class HealthSerializer(serializers.Serializer):
    status = serializers.CharField()


class HealthCheckViewSet(viewsets.GenericViewSet):
    """A simple ViewSet for health check endpoint."""

    permission_classes = [AllowAny]
    serializer_class = HealthSerializer

    def health_check(self, request: Request, *args, **kwargs) -> Response:
        return Response({"status": "ok"}, status=HTTP_200_OK)
