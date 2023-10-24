from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from app.controllers.base import BaseAPI
from app.exceptions.http import HttpException
from app.serializers.status import StatusSerializer
from app.serializers.test_category import TestCategorySerializer
from app.service.test_category import TestCategoryService
from app.utils import helper


class TestCategoryAPI(BaseAPI):
    def get(self, request: Request, id: str) -> Response:
        """
        Get test category data

        :param request: request
        :param id: id
        :return: response
        """
        try:
            # check validations
            helper.check_int('id parameter', id)
            self.check_user_token(request)

            # get test category
            test_category = TestCategoryService().get_test_category_with_id(id)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            TestCategorySerializer(test_category).to_dict(),
            status=status.HTTP_200_OK,
        )


class TestCategoryListAPI(BaseAPI):
    def get(self, request: Request) -> Response:
        """
        Get test category list pagination

        :param request: request
        :return: response
        """
        try:
            # check validation
            self.check_user_token(request, True)

            # search tests
            paging_dict = TestCategoryService().search_test_categories(request.query_params)
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
        Delete test category

        :param request: request
        :return:
        """
        try:
            self.check_user_token(request)

            TestCategoryService().delete_category(request.query_params)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request: Request) -> Response:
        """
        Add test category

        :param request: request
        :return:
        """
        try:
            self.check_user_token(request)

            test_category = TestCategoryService().create_category(request.data)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        return Response(
            TestCategorySerializer(test_category).to_dict(),
            status=status.HTTP_201_CREATED,
        )


class TestCategoryWithTestListAPI(BaseAPI):
    def get(self, request: Request) -> Response:
        """
        Get test category list pagination

        :param request: request
        :return: response
        """
        try:
            # check validation
            self.check_user_token(request, True)

            # search tests
            paging_dict = TestCategoryService().search_test_categories(
                request.query_params, with_tests=True
            )
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
