# Django REST framework modules
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Django modules
from django.contrib.auth import logout
from django.http import HttpRequest

# Third-party modules
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiExample

# Project modules
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer
)
from apps.abstracts.serializers import (
    ErrorResponseSerializer,
    ValidationErrorResponseSerializer,
    SuccessMessageSerializer,
    AuthResponseSerializer
)

# Typing imports
from typing import Any, Dict, Tuple
from django.contrib.auth.models import User
from rest_framework.serializers import Serializer


@extend_schema(
    summary="User registration",
    description="Registers a new user and returns JWT tokens (access and refresh)",
    tags=['Authentication'],
    request=UserRegistrationSerializer,
    responses={
        201: AuthResponseSerializer,
        400: ValidationErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            'Registration request',
            value={
                'username': 'newuser',
                'email': 'user@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'password': 'securepassword123',
                'password_confirm': 'securepassword123'
            },
            request_only=True
        ),
    ]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(
    request: HttpRequest, 
    *args: Any, **kwargs: Any
) -> Response:
    """
    User registration endpoint (JWT access + refresh)

    Params:
        - request: HttpRequest
        - *args
        - **kwargs
    Return:
        - response: Response
    """
    serializer: UserRegistrationSerializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user: User = serializer.save()
        refresh: RefreshToken = RefreshToken.for_user(user)
        return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'User registered successfully'
            }, 
            status=status.HTTP_201_CREATED
        )
    return Response(
        serializer.errors, 
        status=status.HTTP_400_BAD_REQUEST
    )


@extend_schema(
    summary="User login",
    description="Authenticates a user and returns JWT tokens (access and refresh)",
    tags=['Authentication'],
    request=UserLoginSerializer,
    responses={
        200: AuthResponseSerializer,
        400: ValidationErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            'Login request',
            value={
                'username': 'testuser',
                'password': 'password123'
            },
            request_only=True
        ),
    ]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(
    request: HttpRequest, 
    *args: Any, **kwargs: Any
) -> Response:
    """
    User login endpoint (JWT access + refresh)

    Params:
        - request: HttpRequest
        - *args
        - **kwargs
    Return:
        - response: Response
    """
    serializer: UserLoginSerializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user: User = serializer.validated_data['user']
        refresh: RefreshToken = RefreshToken.for_user(user)
        return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Login successful'
            }, 
            status=status.HTTP_200_OK
        )
    return Response(
        serializer.errors, 
        status=status.HTTP_400_BAD_REQUEST
    )


class LogoutView(APIView):
    """
    User logout endpoint — blacklists the refresh token
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="User logout",
        description="Logs out the current authenticated user.",
        tags=['Authentication'],
        responses={
            200: SuccessMessageSerializer,
        }
    )
    def post(
            self, request: HttpRequest, 
            *args: Any, **kwargs: Any
        ) -> Response:
        """
        Logout user. Optionally blacklist refresh token if provided.

        Params:
            - request: HttpRequest
            - *args
            - **kwargs
        Return:
            - response: Response 
        """
        try:
            refresh_token: str | None = request.data.get("refresh")
            
            # If refresh token is provided, blacklist it
            if refresh_token:
                try:
                    token: RefreshToken = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception:
                    # If token is invalid or already blacklisted, continue with logout
                    pass
            
            logout(request)
            return Response(
                {"message": "Successfully logged out"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileView(APIView):
    """
    User profile endpoint
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get user profile",
        description="Returns information about the current authenticated user",
        tags=['Authentication'],
        responses={
            200: UserSerializer,
        }
    )
    def get(
            self, request: HttpRequest, 
            *args: Any, **kwargs: Any
        ) -> Response:
        """
        Get user profile

        Params:
            - request: HttpRequest
            - *args
            - **kwargs
        Return:
            - response: Response 
        """
        serializer: UserSerializer = UserSerializer(request.user)
        return Response(
            serializer.data, 
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Update user profile",
        description="Updates information about the current authenticated user",
        tags=['Authentication'],
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: ValidationErrorResponseSerializer,
        }
    )
    def put(
            self, request: HttpRequest, 
            *args: Any, **kwargs: Any
        ) -> Response:
        """
        Update user profile

        Params:
            - request: HttpRequest
            - *args
            - **kwargs
        Return:
            - response: Response 
        """
        serializer: UserSerializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data, 
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )