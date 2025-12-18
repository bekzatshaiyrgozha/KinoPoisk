# Django modules
from django.contrib.auth import authenticate, get_user_model, logout
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_405_METHOD_NOT_ALLOWED,
)
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.tokens import RefreshToken

# Project modules
from apps.abstracts.serializers import ErrorResponseSerializer
from apps.accounts.serializers import UserSerializer
from apps.accounts.serializers_requests import (
    LoginRequestSerializer,
    RegistrationRequestSerializer,
)
from apps.accounts.serializers_responses import UserSuccessResponseSerializer

User = get_user_model()


class AuthViewSet(ViewSet):
    permission_classes = (AllowAny,)

    @extend_schema(
        request=RegistrationRequestSerializer,
        responses={
            HTTP_201_CREATED: UserSuccessResponseSerializer,
            HTTP_400_BAD_REQUEST: ErrorResponseSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: ErrorResponseSerializer,
        },
    )
    @action(methods=["POST"], detail=False, url_path="register")
    def register(self, request) -> Response:
        serializer = RegistrationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password: str = serializer.validated_data["password"]
        password_confirm: str = serializer.validated_data["password_confirm"]

        if password != password_confirm:
            raise ValidationError({"password_confirm": ["Passwords do not match"]})

        user = User.objects.create_user(
            email=serializer.validated_data["email"],
            first_name=serializer.validated_data["first_name"],
            last_name=serializer.validated_data["last_name"],
            password=password,
        )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "success": True,
                "message": "User registered successfully",
                "data": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=HTTP_201_CREATED,
        )

    @extend_schema(
        request=LoginRequestSerializer,
        responses={
            HTTP_200_OK: UserSuccessResponseSerializer,
            HTTP_400_BAD_REQUEST: ErrorResponseSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: ErrorResponseSerializer,
        },
    )
    @action(methods=["POST"], detail=False, url_path="login")
    def login(self, request) -> Response:
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request=request,
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        if not user:
            raise ValidationError({"non_field_errors": ["Invalid credentials"]})

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "success": True,
                "message": "Login successful",
                "data": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=HTTP_200_OK,
        )

    @extend_schema(
        responses={
            HTTP_200_OK: ErrorResponseSerializer,
            HTTP_400_BAD_REQUEST: ErrorResponseSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: ErrorResponseSerializer,
        },
    )
    @action(
        methods=["POST"],
        detail=False,
        url_path="logout",
        permission_classes=[IsAuthenticated],
    )
    def logout_user(self, request) -> Response:
        refresh_token: str | None = request.data.get("refresh")

        if not refresh_token:
            raise ValidationError({"refresh": ["Refresh token is required"]})

        token = RefreshToken(refresh_token)
        token.blacklist()

        logout(request)

        return Response(
            {
                "success": True,
                "message": "Successfully logged out",
            },
            status=HTTP_200_OK,
        )


class UserProfileViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            HTTP_200_OK: UserSuccessResponseSerializer,
            HTTP_401_UNAUTHORIZED: ErrorResponseSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: ErrorResponseSerializer,
        },
    )
    @action(methods=["GET"], detail=False, url_path="profile")
    def get_profile(self, request) -> Response:
        return Response(
            {
                "success": True,
                "data": UserSerializer(request.user).data,
            },
            status=HTTP_200_OK,
        )

    @extend_schema(
        request=UserSerializer,
        responses={
            HTTP_200_OK: UserSuccessResponseSerializer,
            HTTP_400_BAD_REQUEST: ErrorResponseSerializer,
            HTTP_401_UNAUTHORIZED: ErrorResponseSerializer,
            HTTP_405_METHOD_NOT_ALLOWED: ErrorResponseSerializer,
        },
    )
    @action(methods=["PUT", "PATCH"], detail=False, url_path="profile")
    def update_profile(self, request) -> Response:
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "success": True,
                "message": "Profile updated successfully",
                "data": serializer.data,
            },
            status=HTTP_200_OK,
        )
