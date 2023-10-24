from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from app.controllers.base import BaseAPI
from app.exceptions.http import HttpException
from app.serializers.status import StatusSerializer
from app.serializers.user import UserSerializer
from app.service.user import UserService
from app.utils import helper


class UserDetailAPI(BaseAPI):
    def get(self, request: Request, id: str) -> Response:
        """
        Get user data

        :param request: request
        :param id: user id
        :return: response
        """
        try:
            # check validations
            helper.check_int('id parameter', id)
            self.check_user_token(request)

            # get user
            user = UserService().get_user(id)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            UserSerializer(user).to_dict(),
            status=status.HTTP_200_OK,
        )

    def delete(self, request: Request, id: str) -> Response:
        """
        Delete user

        :param request: request
        :param id: user id
        :return:
        """
        try:
            # check validations
            helper.check_int('id parameter', id)
            self.check_user_token(request, True)

            # delete user
            UserService().delete_user(id)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )
        # success
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserRoleAPI(UserDetailAPI):
    def put(self, request: Request, id: str) -> Response:
        """
        Update user role

        :param request: request
        :param id: user id
        :return: response
        """
        try:
            # check validations
            helper.check_int('id parameter', id)
            self.check_user_token(request, True)

            # update
            UserService().update_user_role(id, request.data)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserListAPI(BaseAPI):
    def get(self, request: Request) -> Response:
        """
        Get user list pagination

        :param request: request
        :return: response
        """
        try:
            # check validation
            self.check_user_token(request, True)

            # search user
            paging_dict = UserService().search_user(request.query_params)
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
