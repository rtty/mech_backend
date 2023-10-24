from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from app.controllers.base import BaseAPI
from app.exceptions.http import HttpException
from app.serializers.rule_version import RuleVersionSerializer
from app.serializers.rule_version_node import RuleVersionNodeSerializer
from app.serializers.status import StatusSerializer
from app.service.rule import RuleVersionService
from app.utils import helper


class RuleVersionDetailAPI(BaseAPI):
    def get(self, request: Request, id: str) -> Response:
        """
        Get rule version by id

        :param request: request
        :param id: rule version id
        :return: response
        """
        try:
            # check id parameter and user token
            helper.check_int('id parameter', id)
            self.check_user_token(request)

            rule_version = RuleVersionService().get_rule_version(id)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            RuleVersionSerializer(rule_version).to_dict(),
            status=status.HTTP_200_OK,
        )

    def delete(self, request: Request, id: str) -> Response:
        """
        Delete rule version, only admin can delete

        :param request: request
        :param id: rule version id
        :return: response
        """
        try:
            # check id parameter and user token - only admin
            helper.check_int('id parameter', id)
            self.check_user_token(request, True)

            RuleVersionService().delete_rule_version(id)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request: Request, id: str) -> Response:
        """
        Patch rule version

        :param request: request
        :param id: rule version id
        :return: response
        """
        try:
            # check id and user token
            helper.check_int('id parameter', id)
            current_user = self.check_user_token(request)

            RuleVersionService().patch_rule_version(id, current_user, request.data)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(status=status.HTTP_204_NO_CONTENT)


class RuleVersionListAPI(BaseAPI):
    def get(self, request: Request, id: str) -> Response:
        """
        Get rule versions

        :param request: request
        :param id: rule id
        :return: response
        """
        # check id parameter and user token
        try:
            helper.check_int('id parameter', id)
            self.check_user_token(request)

            paging_dict = RuleVersionService().search_rule_versions(id, request.query_params)
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

    def post(self, request: Request, id: str) -> Response:
        """
        Create new rule version

        :param request: request
        :param id: rule id
        :return: response
        """
        try:
            # check id parameter and user token
            helper.check_int('id parameter', id)
            current_user = self.check_user_token(request)

            created_rule_version = RuleVersionService().create_new_rule_version(
                id,
                current_user,
                request.data,
            )
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            RuleVersionSerializer(created_rule_version).to_dict(),
            status=status.HTTP_201_CREATED,
        )


class RuleVersionNodeDetailAPI(BaseAPI):
    def get(self, request: Request, id: str, node_id: str) -> Response:
        """
        Get rule version node by id

        :param request: request
        :param id: rule version id
        :param id: rule version node id
        :return: response
        """
        try:
            # check id parameter and user token
            helper.check_int('id parameter', id)
            helper.check_int('node id parameter', node_id)
            self.check_user_token(request)

            rule_version = RuleVersionService().get_rule_version(id)

            rule_version_node = RuleVersionService().get_rule_version_node(node_id, rule_version)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            RuleVersionNodeSerializer(rule_version_node).to_dict(),
            status=status.HTTP_200_OK,
        )


class RuleVersionNodeNotesDetailAPI(BaseAPI):
    def get(self, request: Request, id: str) -> Response:
        """
        Get rule version node by id

        :param request: request
        :param id: rule version id
        :return: response
        """
        try:
            # check id parameter and user token
            self.check_user_token(request)

            rule_version = RuleVersionService().get_rule_version(id)

            rule_version_nodes = RuleVersionService().get_rule_version_nodes(rule_version)
            rule_version_nodes_out = []
            for rule_version_node in rule_version_nodes:
                rule_version_nodes_out.append(
                    RuleVersionNodeSerializer(rule_version_node).to_dict()
                )
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(
            rule_version_nodes_out,
            status=status.HTTP_200_OK,
        )


class RuleVersionModifyAPI(RuleVersionDetailAPI):
    def put(self, request: Request, id: str, modify_type: str) -> Response:
        """
        Update rule versions

        :param request: request
        :param modify_type: modify type
        :return: response
        """
        try:
            # check id validation and user token
            helper.check_int('id parameter', id)
            current_user = self.check_user_token(request)

            # modify
            RuleVersionService().modify_rule_version(id, current_user, modify_type, request.data)

            # success
            if modify_type == 'convert' or modify_type == 'tests':
                rule_version = RuleVersionService().get_rule_version(id)
                return Response(RuleVersionSerializer(rule_version).to_dict())
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

    def post(self, request: Request, id: str, modify_type: str) -> Response:
        """
        Update rule version

        :param request: request
        :param id: rule version id
        :param modify_type: modify type
        :return: response
        """
        try:
            # check id validation and user token
            helper.check_int('id parameter', id)
            current_user = self.check_user_token(request)

            # create new note
            if modify_type == 'clone':
                # clone rule version
                rule_version_id = RuleVersionService().clone_rule_version(current_user, id)

                rule_version = RuleVersionService().get_rule_version(rule_version_id)
                return Response(RuleVersionSerializer(rule_version).to_dict())
            else:
                RuleVersionService().create_new_notes(current_user, modify_type, id, request.data)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(status=status.HTTP_204_NO_CONTENT)


class RuleVersionNodeModifyAPI(RuleVersionDetailAPI):
    def post(self, request: Request, id: str, node_id: str, modify_type: str) -> Response:
        """
        Create rule version node notes

        :param request: request
        :param id: rule version id
        :param node_id: rule version node id
        :param modify_type: modify type
        :return: response
        """
        try:
            # check id validation and user token
            helper.check_int('id parameter', id)
            helper.check_int('node id parameter', node_id)
            current_user = self.check_user_token(request)

            # create new note
            if modify_type == 'notes':
                RuleVersionService().create_new_node_notes(
                    current_user, modify_type, id, node_id, request.data
                )
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )

        # success
        return Response(status=status.HTTP_204_NO_CONTENT)


class RuleVersionTestsAPI(BaseAPI):
    def delete(self, request: Request, id: str, test_id: str) -> Response:
        """
        Delete rule version with tests

        :param request: request
        :param id: rule version id
        :param test_id: test id
        :return: response
        """
        try:
            # check id validation and user token
            helper.check_int('id parameter', id)
            helper.check_int('testId parameter', test_id)
            current_user = self.check_user_token(request)

            # modify
            RuleVersionService().delete_rule_version_test(current_user, id, test_id)

            return Response(status=status.HTTP_204_NO_CONTENT)
        except HttpException as e:
            return Response(
                StatusSerializer(e.code, e.message).to_dict(),
                status=e.get_http_status(),
            )
