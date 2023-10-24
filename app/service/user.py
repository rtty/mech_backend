from typing import Any, Dict, List, Optional, Union

from django.db import IntegrityError, transaction
from django.http.request import QueryDict

from app.exceptions.http import HttpException
from app.models import User
from app.serializers.paging import PagingSerializer
from app.serializers.query import QuerySerializer
from app.serializers.user import UserSerializer
from app.utils import helper


class UserService:
    """
    user service

    get_user(): get user
    get_user_by_email(): get user by email
    get_user_info_by_email(): get user by email
    check_user_exists(): get user exists boolean
    delete_user(): delete user
    update_user_role(): update user role
    create_new_user_from_azure_token(): create new user from azure token
    get_user_list(): get user list
    get_user_total(): get user total count
    search_user(): search user with filter
    """

    def get_user(self, id: Union[int, str]) -> User:
        """
        Get user
        :param id: user id
        :return: user
        """
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            raise HttpException(404, 'User not found')

    def get_user_by_email(self, email: str) -> User:
        """
        Get user
        :param email: user email
        :return: user
        """
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            raise HttpException(404, 'User not found')

    def get_user_info_by_email(self, email: str) -> Dict[str, Optional[Union[str, int]]]:
        """
        Get user
        :param email: user email
        :return: user info
        """
        user = self.get_user_by_email(email)
        return UserSerializer(user).to_dict()

    def check_user_exists(self, id):
        """
        check user exists
        :param id: user id
        :return: boolean
        """
        exists = True

        try:
            self.get_user(id)
        except HttpException:
            exists = False

        return exists

    def check_user_exists_by_email(self, email: str) -> bool:
        """
        check user exists
        :param id: user id
        :return: boolean
        """
        exists = True

        try:
            self.get_user_by_email(email)
        except HttpException:
            exists = False

        return exists

    def delete_user(self, id: str):
        """
        Delete user
        :param id: user id
        :return: void
        """
        user = self.get_user(id)
        user.delete()

    def update_user_role(self, id: str, data: Dict[str, str]) -> None:
        """
        update user role
        :param id: user id
        :param data: data
        :return: void
        """
        # get user
        user = self.get_user(id)

        if data is None:
            raise HttpException(400, 'no payload')

        # check role validation
        role = data.get('newRole')

        if role is None or role not in ['standard', 'admin']:
            raise HttpException(400, "newRole should be 'standard' or 'admin', current: " + role)

        # update user
        user.role = role
        user.save()

    def create_new_user_from_azure_token(self, userInfo):
        """
        create new user
        :param userInfo: data
        :return: user
        """
        try:
            # create workspace and insert owner to first member
            with transaction.atomic():
                created_user = User.objects.create(
                    name=userInfo.get('name'),
                    email=userInfo.get('unique_name'),
                    role=userInfo.get('role'),
                )
        except IntegrityError:
            raise HttpException(409, userInfo.get('name') + ' already exists')

        return UserSerializer(created_user).to_dict()

    def get_user_list(
        self, offset: int, limit: int, sort_by: str
    ) -> List[Dict[str, Optional[Union[str, int]]]]:
        """
        Get user list by options
        :param offset: offset
        :param limit: limit
        :param sort_by: sort by
        :return: user list
        """
        results = []
        users = User.objects.order_by(sort_by)[offset : offset + limit]

        for user in list(users):
            results.append(UserSerializer(user).to_dict())

        return results

    def get_user_total(self) -> int:
        """
        Get user total count
        :return: count
        """
        return User.objects.count()

    def search_user(self, query: QueryDict) -> Dict[str, Any]:
        """
        search user
        :param query: query
        :return: paging dictionary
        """
        # get queries
        query = QuerySerializer(query)

        limit = query.get('limit', 10000000000, 'int')
        offset = query.get('offset', 0, 'int')
        sort_by = query.get('sortBy', 'name')
        sort_order = query.get('sortOrder', 'asc')

        # check sort by value
        helper.check_choices('sortBy', sort_by, ['name', 'email', 'role'])
        helper.check_choices('sortOrder', sort_order, ['asc', 'desc'])

        # set desc sort by
        if sort_order == 'desc':
            sort_by = '-' + sort_by

        # get users
        users = self.get_user_list(offset, limit, sort_by)

        # get total
        total = self.get_user_total()

        return PagingSerializer(offset, limit, total, users).to_dict()
