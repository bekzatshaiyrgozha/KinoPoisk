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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Project modules
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer
)

# Typing imports
from typing import Any, Dict, Tuple
from django.contrib.auth.models import User
from rest_framework.serializers import Serializer


@swagger_auto_schema(
    method='post',
    request_body=UserRegistrationSerializer,
    responses={
        status.HTTP_201_CREATED: openapi.Response('User registered', UserSerializer),
        status.HTTP_400_BAD_REQUEST: openapi.Response('Invalid data')
    }
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


@swagger_auto_schema(
    method='post',
    request_body=UserLoginSerializer,
    responses={
        status.HTTP_200_OK: openapi.Response('Login successful', UserSerializer),
        status.HTTP_400_BAD_REQUEST: openapi.Response('Invalid credentials')
    }
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

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token')
            },
            required=['refresh']
        ),
        responses={
            status.HTTP_200_OK: openapi.Response('Successfully logged out'),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Invalid or missing token')
        }
    )
    def post(
            self, request: HttpRequest, 
            *args: Any, **kwargs: Any
        ) -> Response:
        """
        Blacklist the refresh token

        Params:
            - request: HttpRequest
            - *args
            - **kwargs
        Return:
            - response: Response 
        """
        try:
            refresh_token: str | None = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token: RefreshToken = RefreshToken(refresh_token)
            token.blacklist()
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

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: openapi.Response('User profile', UserSerializer)
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

    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response('Profile updated', UserSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Invalid data')
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