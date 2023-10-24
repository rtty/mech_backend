from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from app.controllers.base import BaseAPI
from app.exceptions.http import HttpException
from app.serializers.status import StatusSerializer
from app.serializers.test import TestSerializer
from app.service.test import TestService
from app.utils import helper


class TestAPI(BaseAPI):
    def get(self, request):
        """
        Get tests

        :param: request request
        :return: response
        """
        try:
            # check user token
            self.check_user_token(request)

            result = TestService().get_specific_tests(request.query_params)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        return Response(
            result,
            status=status.HTTP_200_OK,
        )

    def get(self, request: Request, id: str) -> Response:
        """
        Get test data

        :param request: request
        :param id: id
        :return: response
        """
        try:
            # check validations
            helper.check_int('id parameter', id)
            self.check_user_token(request)

            # get test
            test = TestService().get_test_with_id(id)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            TestSerializer(test).to_dict(),
            status=status.HTTP_200_OK,
        )


class TestListAPI(BaseAPI):
    def get(self, request: Request) -> Response:
        """
        Get test list pagination

        :param request: request
        :return: response
        """
        try:
            # check validation
            self.check_user_token(request, True)

            # search tests
            paging_dict = TestService().search_tests(request.query_params)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            paging_dict,
            status=status.HTTP_200_OK,
        )

    def delete(self, request: Request) -> Response:
        """
        Delete test

        :param request: request
        :return:
        """
        try:
            self.check_user_token(request)

            TestService().delete_specific_test(request.query_params)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request: Request) -> Response:
        """
        Add test to test category

        :param request: request
        :return:
        """
        try:
            self.check_user_token(request)

            test = TestService().add_test(request.data)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        return Response(TestSerializer(test).to_dict(), status=status.HTTP_201_CREATED)
