# Python modues 
from typing import Any,Optional

#Django Modules 
from django.contrib.auth import logout,get_user_model
from django.http import HttpRequest

# Django REST Framework
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_405_METHOD_NOT_ALLOWED
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

User =get_user_model()

class AuthViewSet(ViewSet):
    """
    VIew set for haning auth-related endpoints related to the registration,logout,login
    """
    permmission_classes=(AllowAny,)

    @extend_schema(
        summary="User Registration",
        request=UserRegistrationSerializer,
        responses={
            HTTP_201_CREATED:OpenApiResponse(
                description="Succesful registration",
                response=AuthResponseSerializer
            ),
            HTTP_400_BAD_REQUEST:OpenApiResponse(
                description="Bad request",
                response=ValidationErrorResponseSerializer
            ),
        }
    )
    @action(
        methods=("POST",),
        detail=False,
        url_path="register",
        url_name="register",
    )
    def register(
        self,
        request:DRFRequest,
        *args:tuple[Any,...],
        **kwargs:dict[str,Any]
    )->DRFResponse:
        """
       Holly shit this is docstrings  
       Handle POST request for user registration 

       Parameters:
       reqeust:DrfRequest, 


       Return 
       a respone containig user data and jwt tokens
        """
        serializer:UserRegistrationSerializer=UserRegistrationSerializer(
            data=request.data
            )
        serializer.is_valid(raise_exception=True)
        
        user: User = serializer.save()
        refresh_token:RefreshToken=RefreshToken.for_user(user)
        access_token:str=str(refresh_token.access_token)

        return DRFResponse(
            data={
                "user":UserSerializer(user).data, 
                "refresh":str(refresh_token),
                "access":access_token, 
                "message":"User registred sucessfully",
            },
            status=HTTP_201_CREATED
        )
    

    @extend_schema(
        summary="User Login", 
        request=UserLoginSerializer, 
        responses={
            HTTP_200_OK:OpenApiResponse(
                description="Succesfully logined",
                response=AuthResponseSerializer,
            ),
            HTTP_400_BAD_REQUEST:OpenApiResponse(
                description="Bad request",
                response=ValidationErrorResponseSerializer,
            ),
            HTTP_405_METHOD_NOT_ALLOWED:OpenApiResponse(
                description="Method not allowed",
                response=ValidationErrorResponseSerializer,
            )
        }
    )
    @action(
        methods=["POST"],
        detail=False,
        url_path="login",
        url_name="login",
    )
    def login(
        self,
        request:DRFRequest,
        *args:tuple[Any,...],
        **kwargs:dict[str,Any],
    )->DRFResponse:
        """
       User login get in the input request with the DrfRequest 

       in output get response using data and jwt tokens
        """
        seralizer:UserLoginSerializer=UserLoginSerializer(data=request.data)
        seralizer.is_valid(raise_exception=True)
        user:User=seralizer.validate_data.pop("user")

        refresh_token:RefreshToken=RefreshToken.for_user(user)
        acccess_token:str=str(refresh_token.access_token)

        return DRFResponse(
            data={
                "user":UserSerializer(user).data, 
                "refresh":str(refresh_token),
                "access":acccess_token,
                "message":"Login suceessfull!!",
            },
            status=HTTP_200_OK
        )
    
    