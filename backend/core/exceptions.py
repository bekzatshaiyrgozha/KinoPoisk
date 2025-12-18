from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    MethodNotAllowed,
    NotAuthenticated,
    PermissionDenied,
    NotFound,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_405_METHOD_NOT_ALLOWED,
)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, ValidationError):
        return Response(
            {
                "success": False,
                "message": "Validation error",
                "errors": exc.detail,
            },
            status=HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, MethodNotAllowed):
        return Response(
            {
                "success": False,
                "message": f"Method '{exc.method}' is not allowed.",
            },
            status=HTTP_405_METHOD_NOT_ALLOWED,
        )

    if isinstance(exc, NotAuthenticated):
        return Response(
            {
                "success": False,
                "message": "Authentication credentials were not provided.",
            },
            status=HTTP_401_UNAUTHORIZED,
        )

    if isinstance(exc, PermissionDenied):
        return Response(
            {
                "success": False,
                "message": "You do not have permission to perform this action.",
            },
            status=HTTP_403_FORBIDDEN,
        )

    if isinstance(exc, NotFound):
        return Response(
            {
                "success": False,
                "message": "Resource not found.",
            },
            status=HTTP_404_NOT_FOUND,
        )

    if response is not None:
        response.data = {
            "success": False,
            "message": response.data.get("detail", "Error"),
        }

    return response
