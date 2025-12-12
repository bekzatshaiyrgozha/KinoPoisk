from django.urls import path
from rest_framework.routers import DefaultRouter

# Project modules
from .views import (
    AuthViewSet,
    UserProfileViewSet,
)

app_name = "accounts"

urlpatterns = [
    
    path("register/", AuthViewSet.as_view({"post": "register"}), name="register"),
    path("login/", AuthViewSet.as_view({"post": "login"}), name="login"),
    path("logout/", AuthViewSet.as_view({"post": "logout"}), name="logout"),
    
    path("profile/", UserProfileViewSet.as_view({
        "get": "get_profile",
        "put": "update_profile",
        "patch": "update_profile"
    }), name="profile"),
]