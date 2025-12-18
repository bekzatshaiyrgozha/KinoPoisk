# Django modules
from django.urls import path

# Project modules
from .views import (
    AuthViewSet,
    UserProfileViewSet,
)

urlpatterns = [
    path("register/", AuthViewSet.as_view({"post": "register"}), name="register"),
    path("login/", AuthViewSet.as_view({"post": "login"}), name="login"),
    path("logout/", AuthViewSet.as_view({"post": "logout_user"}), name="logout"),
    path(
        "profile/",
        UserProfileViewSet.as_view(
            {"get": "get_profile", "put": "update_profile", "patch": "update_profile"}
        ),
        name="profile",
    ),
]
