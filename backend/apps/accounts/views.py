# Python modues
from typing import Any, Optional

# Django Modules
from django.contrib.auth import logout, get_user_model

# Django REST Framework
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
)
from rest_framework.decorators import action

# Third-party modules
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse

# Project modules
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
)
from apps.abstracts.serializers import (
    ErrorResponseSerializer,
    ValidationErrorResponseSerializer,
    SuccessMessageSerializer,
    AuthResponseSerializer,
)

User = get_user_model()


class AuthViewSet(ViewSet):
    """
    ViewSet for handling auth-related endpoints: registration, login, and logout.
    """

    permission_classes = (AllowAny,)

    @extend_schema(
        summary="User Registration",
        request=UserRegistrationSerializer,
        responses={
            HTTP_201_CREATED: OpenApiResponse(
                description="Successful registration", response=AuthResponseSerializer
            ),
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Bad request", response=ValidationErrorResponseSerializer
            ),
            HTTP_405_METHOD_NOT_ALLOWED: OpenApiResponse(
                description="Method not allowed",
                response=ErrorResponseSerializer,
            ),
        },
    )
    @action(
        methods=("POST",),
        detail=False,
        url_path="register",
        url_name="register",
    )
    def register(
        self, request: DRFRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> DRFResponse:
        """
        Handle POST request for user registration.

        Parameters:
            request (DRFRequest): The request object containing registration data.

        Returns:
            DRFResponse: A response containing user data and JWT tokens.
        """
        serializer: UserRegistrationSerializer = UserRegistrationSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        user: User = serializer.save()
        refresh_token: RefreshToken = RefreshToken.for_user(user)
        access_token: str = str(refresh_token.access_token)

        return DRFResponse(
            data={
                "user": UserSerializer(user).data,
                "refresh": str(refresh_token),
                "access": access_token,
                "message": "User registered successfully",
            },
            status=HTTP_201_CREATED,
        )

    @extend_schema(
        summary="User Login",
        request=UserLoginSerializer,
        responses={
            HTTP_200_OK: OpenApiResponse(
                description="Successfully logged in",
                response=AuthResponseSerializer,
            ),
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Bad request",
                response=ErrorResponseSerializer,
            ),
            HTTP_405_METHOD_NOT_ALLOWED: OpenApiResponse(
                description="Method not allowed",
                response=ValidationErrorResponseSerializer,
            ),
        },
    )
    @action(
        methods=("POST",),
        detail=False,
        url_path="login",
        url_name="login",
    )
    def login(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        Handle POST request for user login.

        Parameters:
            request (DRFRequest): The request object containing login credentials.

        Returns:
            DRFResponse: A response containing user data and JWT tokens.
        """
        seralizer: UserLoginSerializer = UserLoginSerializer(data=request.data)
        seralizer.is_valid(raise_exception=True)
        user: User = seralizer.validated_data.pop("user")

        refresh_token: RefreshToken = RefreshToken.for_user(user)
        acccess_token: str = str(refresh_token.access_token)

        return DRFResponse(
            data={
                "user": UserSerializer(user).data,
                "refresh": str(refresh_token),
                "access": acccess_token,
                "message": "Login successful",
            },
            status=HTTP_200_OK,
        )

    @extend_schema(
        summary="User logout",
        responses={
            HTTP_200_OK: OpenApiResponse(
                description="Successfully logged out",
                response=SuccessMessageSerializer,
            ),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description="Unauthorized - Authentication credentials were not provided.",
                response=ErrorResponseSerializer,
            ),
            HTTP_403_FORBIDDEN: OpenApiResponse(
                description="Forbidden - You do not have permission to perform this action.",
                response=ErrorResponseSerializer,
            ),
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Bad request",
                response=ErrorResponseSerializer,
            ),
            HTTP_405_METHOD_NOT_ALLOWED: OpenApiResponse(
                description="Method not allowed",
                response=ErrorResponseSerializer,
            ),
        },
    )
    @action(
        methods=("POST",),
        detail=False,
        url_path="logout",
        url_name="logout",
        permission_classes=(IsAuthenticated,),
    )
    def logout(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        Handle POST request for user logout.
        Blacklists the refresh token if provided.

        Parameters:
            request (DRFRequest): The request object containing the refresh token.

        Returns:
            DRFResponse: A success message.
        """
        try:
            refresh_token: Optional[str] = request.data.get("refresh")

            if refresh_token:
                try:
                    token: RefreshToken = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception:
                    pass

            logout(request)

            return DRFResponse(
                data={"message": "Successfully logged out"},
                status=HTTP_200_OK,
            )
        except Exception as e:
            return DRFResponse(data={"error": str(e)}, status=HTTP_400_BAD_REQUEST)


class UserProfileViewSet(ViewSet):
    """
    Operation for handling user profile
    """

    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary="Get User Profile",
        responses={
            HTTP_200_OK: OpenApiResponse(
                description="Return the profile data",
                response=UserSerializer,
            ),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description="Unauthorized - Authentication credentials were not provided.",
                response=ErrorResponseSerializer,
            ),
            HTTP_403_FORBIDDEN: OpenApiResponse(
                description="Forbidden - You do not have permission to perform this action.",
                response=ErrorResponseSerializer,
            ),
            HTTP_405_METHOD_NOT_ALLOWED: OpenApiResponse(
                description="Method not allowed",
                response=ErrorResponseSerializer,
            ),
        },
    )
    @action(
        methods=("GET",),
        detail=False,
        url_path="profile",
        url_name="profile",
    )
    def get_profile(
        self, request: DRFRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> DRFResponse:
        """
        Retrieve the authenticated user's profile.

        Returns:
            DRFResponse: The user's profile data.
        """
        user: User = request.user

        return DRFResponse(
            data=UserSerializer(user).data,
            status=HTTP_200_OK,
        )

    @extend_schema(
        summary="Updating the Profile User",
        request=UserSerializer,
        responses={
            HTTP_403_FORBIDDEN: OpenApiResponse(
                description="Forbidden - You do not have permission to perform this action.",
                response=ErrorResponseSerializer,
            ),
            HTTP_405_METHOD_NOT_ALLOWED: OpenApiResponse(
                description="Method not allowed",
                response=ErrorResponseSerializer,
            ),
            HTTP_200_OK: OpenApiResponse(
                description="Returns the updated user profile",
                response=UserSerializer,
            ),
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Bad request due to invalid data",
                response=ValidationErrorResponseSerializer,
            ),
            HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description="Unauthorized to perform this action",
                response=ErrorResponseSerializer,
            ),
        },
    )
    @action(
        methods=("PUT", "PATCH"),
        detail=False,
        url_path="profile",
        url_name="update-profile",
    )
    def update_profile(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        """
        Updating the user Profile using this endpoint,
        getting the result with the updaed the user profile
        """

        serializer: UserSerializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return DRFResponse(
            data=serializer.data,
            status=HTTP_200_OK,
        )
