from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from app.controllers.base import BaseAPI
from app.exceptions.http import HttpException
from app.serializers.status import StatusSerializer
from app.serializers.workspace import WorkspaceSerializer
from app.serializers.workspace_expanded import WorkspaceExpandedSerializer
from app.service.workspace import WorkspaceService
from app.utils import helper


class WorkspaceDetailAPI(BaseAPI):
    def get(self, request: Request, id: str) -> Response:
        """
        Get workspace detail only user is a member

        :param id: workspace id
        :return: response
        """
        try:
            # check user and parameter validation
            helper.check_int('id parameter', id)
            current_user = self.check_user_token(request)

            # check is member
            WorkspaceService().check_is_member(id, current_user.get('id'))

            # get workspace
            workspace = WorkspaceService().get_workspace(id)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            WorkspaceExpandedSerializer(workspace).to_dict(),
            status=status.HTTP_200_OK,
        )

    def delete(self, request: Request, id: str) -> Response:
        """
        Delete workspace

        :param request: request
        :param id: workspace id
        :return: response
        """
        try:
            # check user and parameter validation
            helper.check_int('id parameter', id)
            current_user = self.check_user_token(request)

            # delete
            WorkspaceService().delete_workspace(id, current_user)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request: Request, id: str) -> Response:
        """
        Update workspace

        :param request: request
        :param id: workspace id
        :return: response
        """
        try:
            # check user and parameter validation
            helper.check_int('id parameter', id)
            current_user = self.check_user_token(request)

            # update
            WorkspaceService().update_workspace(id, current_user, request.data)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(status=status.HTTP_204_NO_CONTENT)


class WorkspaceListAPI(BaseAPI):
    def get(self, request: Request) -> Response:
        """
        Get workspace list

        :param request: request
        :return: response
        """
        try:
            # check user token
            current_user = self.check_user_token(request)

            # search workspaces
            paging_dict = WorkspaceService().search_workspaces(current_user, request.query_params)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        return Response(
            paging_dict,
            status=status.HTTP_200_OK,
        )

    def post(self, request: Request) -> Response:
        """
        Create new workspace

        :param request: request
        :return: response
        """
        try:
            # check validation and get current user dictionary
            current_user = self.check_user_token(request)

            # create
            created_workspace = WorkspaceService().create_new_workspace(current_user, request.data)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            WorkspaceSerializer(created_workspace).to_dict(),
            status=status.HTTP_201_CREATED,
        )


class WorkspaceCopyAPI(BaseAPI):
    def post(self, request: Request, id: str) -> Response:
        """
        Copy workspace

        :param request: request
        :param id: workspace id
        :return: response
        """
        try:
            # check user and parameter validation
            helper.check_int('id parameter', id)
            current_user = self.check_user_token(request)

            # copy
            copied_workspace = WorkspaceService().copy_workspace(id, current_user, request.data)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            WorkspaceSerializer(copied_workspace).to_dict(),
            status=status.HTTP_201_CREATED,
        )
