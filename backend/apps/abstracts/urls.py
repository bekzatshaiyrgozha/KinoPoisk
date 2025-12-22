from django.urls import path
from .views import HealthCheckViewSet


urlpatterns = [
    path(
        "health/",
        HealthCheckViewSet.as_view({"get": "health_check"}),
        name="health-check",
    ),
]
