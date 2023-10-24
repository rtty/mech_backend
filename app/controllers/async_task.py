from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from app.controllers.base import BaseAPI
from app.exceptions.http import HttpException
from app.serializers.async_task import AsyncTaskSerializer
from app.serializers.status import StatusSerializer
from app.service.async_task import AsyncTaskService
from app.utils import helper


class AsyncTaskListAPI(BaseAPI):
    def get(self, request: Request) -> Response:
        """
        Gets async task list

        :param request: request
        :return: response
        """
        try:
            # check user token
            self.check_user_token(request)

            # search project
            running = AsyncTaskService().get_running_tasks()
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            dict(results=[AsyncTaskSerializer(task).to_dict() for task in running]),
            status=status.HTTP_200_OK,
        )


class AsyncTaskDetailAPI(BaseAPI):
    def get(self, request: Request, id: str) -> Response:
        """
        Gets async task details list

        :param request: request
        :return: response
        """

        try:
            helper.check_int('id parameter', id)
            self.check_user_token(request)

            task = AsyncTaskService().get_async_task(id)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )
        # success
        return Response(
            AsyncTaskSerializer(task).to_dict(),
            status=status.HTTP_200_OK,
        )


class AsyncTaskCancelAPI(BaseAPI):
    def put(self, request: Request, id: str) -> Response:
        """
        Cancel async task

        :param request: request
        :return: response

        """
        try:
            helper.check_int('id parameter', id)
            current_user = self.check_user_token(request)
            task = AsyncTaskService().cancel_async_task(id, current_user)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )
        # success
        return Response(AsyncTaskSerializer(task).to_dict(), status=status.HTTP_200_OK)
