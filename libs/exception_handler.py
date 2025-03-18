import logging
from pydantic import ValidationError as PydanticException
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import exception_handler
from . import exceptions as lib_exceptions

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):

    if isinstance(exc, PydanticException):
        logger.info(f'Pydantic ValidationError: {exc}')
        return Response({"detail": exc.errors(), "type": "PydanticException"}, status=status.HTTP_400_BAD_REQUEST)

    elif isinstance(exc, lib_exceptions.ServiceExceptions):
        logger.info(f'Service Exception: {exc}')
        return Response({"detail": str(exc), "type": exc.__class__.__name__}, status=exc.status_code)

    return exception_handler(exc, context)  # handle 405 and raises 500
