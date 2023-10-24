from rest_framework import status
from rest_framework.response import Response

from app.controllers.base import BaseAPI
from app.exceptions.http import HttpException
from app.serializers.status import StatusSerializer
from app.service.tests import TestsService


class TestsAPI(BaseAPI):
    def get(self, request):
        """
        Get tests

        :param: request reuqest
        :return: response
        """
        try:
            # check user token
            self.check_user_token(request)

            result = TestsService().get_specific_tests(request.query_params)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        return Response(
            result,
            status=status.HTTP_200_OK,
        )

    def delete(self, request):
        """
        Delete test

        :param request: request
        :return:
        """
        try:
            self.check_user_token(request)

            TestsService().delete_specific_test(request.query_params)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request):
        """
        Add test to test category

        :param request: request
        :return:
        """
        try:
            self.check_user_token(request)

            TestsService().add_test(request.data)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
