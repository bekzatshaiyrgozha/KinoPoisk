# Django module
from django.urls import path

# Project modules
from .views import (
    register,
    login_view,
    LogoutView,
    UserProfileView,
)

app_name = "accounts"

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", UserProfileView.as_view(), name="user_profile"),
]
