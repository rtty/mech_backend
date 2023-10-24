from typing import Dict

from rest_framework.request import Request
from rest_framework.views import APIView

from app.exceptions.http import HttpException
from app.service.user import UserService
from app.service.validateToken import validate_jwt


class BaseAPI(APIView):
    def check_user_token(self, request: Request, only_admin: bool = False) -> Dict[str, str | int]:
        """
        Check token validation

        :param request: request
        :param only_admin: accept only admin
        :return: current user as dictionary
        """
        token = request.headers.get('Authorization')
        if token is None:
            raise HttpException(401, 'Token is missing')

        token = token.replace('Bearer ', '')

        # decode token
        try:
            current_user = validate_jwt(token)
        except Exception:
            raise HttpException(401, 'Invalid user token')

        # check user exists
        if not current_user:
            raise HttpException(404, "User doesn't exist")

        # check user exists
        if not UserService().check_user_exists_by_email(current_user.get('unique_name')):
            print(1)
            current_user['role'] = 'admin'
            logged_user = UserService().create_new_user_from_azure_token(current_user)
        else:
            print(2)
            logged_user = UserService().get_user_info_by_email(current_user.get('unique_name'))

        # check admin
        if only_admin and logged_user.get('role') != 'admin':
            raise HttpException(403, 'Only Admin users are allowed')

        return logged_user
