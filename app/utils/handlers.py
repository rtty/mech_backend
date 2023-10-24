import traceback
from typing import Any, Dict

from django.db.utils import DataError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from app.serializers.status import StatusSerializer


def custom_exception_handler(exc: Exception, context: Dict[str, Any]) -> Response:
    """
    Custom exception handler
    Unhandled exceptions will be returned with 500 error

    :param exc: exception
    :param context: context
    :return: response
    """
    response = exception_handler(exc, context)

    if response is not None:
        response.data['code'] = response.status_code
        response.data['message'] = response.status_text

    traceback.print_exc()
    messages = []

    for arg in exc.args:
        if type(arg) != str:
            messages.append(str(arg))
        else:
            messages.append(arg)

    message = ' '.join(messages)

    if type(exc) == DataError:
        # data validation error
        return Response(
            StatusSerializer(400, message).to_dict(),
            status=status.HTTP_400_BAD_REQUEST,
        )

    else:
        # others
        return Response(
            StatusSerializer(500, message).to_dict(),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
