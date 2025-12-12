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
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_401_UNAUTHORIZED
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
    permission_classes=(AllowAny,)

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
        methods=("POST",),
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
        user:User=seralizer.validated_data.pop("user")

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
    
    @extend_schema(
        summary="User logout",
        responses={
            HTTP_200_OK:OpenApiResponse(
                description="Succesfully logged out",
                response=SuccessMessageSerializer,
            
            ),
            HTTP_400_BAD_REQUEST:OpenApiResponse(
                description="Bad request",
                response=ErrorResponseSerializer,
            ),
        }
    )
    @action(
        methods=("POST",),
        detail=False,
        url_path="logout",
        url_name="logout",
        permission_classes=(IsAuthenticated,)
    )
    def logout(
        self,
        request:DRFRequest,
        *args:tuple[Any,...],
        **kwargs:dict[str,Any],
    )->DRFResponse:
        """
        handling post request to logout 
        using DrfRequest 

        and in the end we get the suceesfiluu logout 

        """
        try:
            refresh_token:Optional[str]=request.data.get("refresh")

            if refresh_token:
                try:
                    token:RefreshToken=RefreshToken(refresh_token)
                    token.blacklist()
                except Exception:
                    pass 
            
            logout(request)

            return DRFResponse(
                data={"message":"Suceesfully logout from the KinoPoisk"},
                status=HTTP_200_OK
                    
            )
        except Exception as e:
            return DRFResponse(
                data={"error":str(e)},
                status=HTTP_400_BAD_REQUEST
            )


class UserProfileViewSet(ViewSet):
    """
   Operation for handling user profile
    """
    permission_classes = (IsAuthenticated,)
    
    @extend_schema(
        summary="Get User Profile",
        responses={
            HTTP_200_OK:OpenApiResponse(
                description="Return the profile data",
                response=UserSerializer,
            ),
        }
    )
    @action(
        methods=("GET",),
        detail=False,
        url_path="profile",
        url_name="profile",
    )
    def get_profile(
        self,
        request:DRFRequest,
        *args:tuple[Any,...],
        **kwargs:dict[str,Any]
    )->DRFResponse:
        """
       this is endpoint for 
       getting userproflie 
       and in the end you get the user profile like the data
        """
        user:User=request.user 

        return DRFResponse(
            data=UserSerializer(user).data,
            status=HTTP_200_OK,
        )
    @extend_schema(
        summary="Updating the Profile User",
        request=UserSerializer,
        responses={
            HTTP_200_OK:OpenApiResponse(
                description="Returns the updated user profile",
                response=UserSerializer,
            ),
            HTTP_400_BAD_REQUEST:OpenApiResponse(
                description="Bad request due to invalid data",
                response=ValidationErrorResponseSerializer,
            ),
            HTTP_401_UNAUTHORIZED:OpenApiResponse(
                description="Unauthorized to perform this action",
                response=ErrorResponseSerializer,
            ),
        }
    )
    @action(
        methods=("PUT","PATCH"),
        detail=False,
        url_path="profile",
        url_name="update-profile",
    )
    def update_profile(
        self,
        request:DRFRequest,
        *args:tuple[Any,...],
        **kwargs:dict[str,Any],
    )->DRFResponse:
        """
        Updating the user Profile using this endpoint, 
        getting the result with the updaed the user profile
        """

        serializer:UserSerializer=UserSerializer(
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