from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from app.controllers.base import BaseAPI
from app.exceptions.http import HttpException
from app.serializers.status import StatusSerializer
from app.service.rule_function import RuleFunctionService


class NodeFunctionAPI(BaseAPI):
    """
    Node function controller
    """

    def post(self, request: Request, function: str) -> Response:
        """
        Parse rule text

        :param request: request
        :param function: parse function
        :return: Response
        """
        try:
            # check user token
            self.check_user_token(request)

            # parse rule text
            result = RuleFunctionService().parse_node_text(request.data, function)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            result.to_dict(),
            status=status.HTTP_200_OK,
        )

    def get(self, request: Request, function: str) -> Response:
        """
        Get specific test

        :param request: request
        :param function: function
        :return: Response
        """
        try:
            # check user token
            self.check_user_token(request)

            # get test by category
            result = RuleFunctionService().get_node_test_by_category(request.query_params, function)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            result,
            status=status.HTTP_200_OK,
        )
