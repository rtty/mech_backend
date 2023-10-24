from typing import Any, Dict, List, Optional, Union

from django.db import IntegrityError, transaction
from django.http.request import QueryDict

from app.exceptions.http import HttpException
from app.models import (Workspace, WorkspacesMember, WorkspacesProject,
                        WorkspacesRule)
from app.serializers.paging import PagingSerializer
from app.serializers.query import QuerySerializer
from app.serializers.workspace import WorkspaceSerializer
from app.service.project import ProjectService
from app.service.rule import RuleService
from app.service.user import UserService
from app.utils import helper


class WorkspaceService:
    """
    workspace service

    get_workspace(): get single workspace
    delete_workspace(): delete single workspace
    get_workspace_list(): get workspace list
    get_workspace_total(): get workspace total count
    search_workspaces(): search workspace list with pagination
    create_new_workspace(): create new workspace
    update_workspace(): update workspace
    delete_and_insert_members(): delete existing members and insert members
    delete_and_insert_projects(): delete existing projects and insert projects
    delete_and_insert_rules(): delete existing rules and insert rules
    copy_workspace(): copy workspace and associates
    check_is_member(): check the user is a member of the workspace
    add_members(): add member to workspace
    add_projects(): add project to workspace
    add_rules(): add rule to workspace
    """

    def get_workspace(self, id: Union[int, str]) -> Workspace:
        """
        Get workspace
        :param id: workspace id
        :return: workspace
        """
        try:
            return Workspace.objects.get(id=id)
        except Workspace.DoesNotExist:
            raise HttpException(404, 'Workspace not found')

    def delete_workspace(self, id: str, user_dict: Dict[str, Optional[Union[str, int]]]):
        """
        Delete workspace
        :param id: workspace id
        :param user_dict: user dictionary
        :return: void
        """
        # get workspace
        workspace = self.get_workspace(id)

        # check owner or super user
        if user_dict.get('id') != workspace.user.id and user_dict.get('role') != 'admin':
            raise HttpException(403, 'Only Admin user or owner can delete workspace')

        # get associates
        workspace_rules = WorkspacesRule.objects.filter(workspace=workspace)
        workspace_members = WorkspacesMember.objects.filter(workspace=workspace)
        workspace_projects = WorkspacesProject.objects.filter(workspace=workspace)

        # delete
        with transaction.atomic():
            workspace_projects.delete()
            workspace_members.delete()
            workspace_rules.delete()
            workspace.delete()

    def get_workspace_list(
        self, offset: int, limit: int, order: str, user_id: int
    ) -> List[Dict[str, Union[int, List[int], str]]]:
        """
        Get workspace list with current user
        :param offset: offset
        :param limit: limit
        :param order: order direction
        :param user_id: current user id
        :return: workspace list
        """
        sort_by = 'name' if order == 'asc' else '-name'

        # get user
        user = UserService().get_user(user_id)

        # get members
        workspace_members = WorkspacesMember.objects.filter(user=user)

        # get workspace ids
        workspace_ids = []

        for workspace_member in workspace_members:
            workspace_ids.append(workspace_member.workspace.id)

        # filter workspaces
        results = []
        workspaces = Workspace.objects.filter(id__in=workspace_ids).order_by(sort_by)[
            offset : offset + limit
        ]

        for workspace in list(workspaces):
            results.append(WorkspaceSerializer(workspace).to_dict())

        return results

    def get_workspace_total(self) -> int:
        """
        Get workspace total count
        :return: total count
        """
        return Workspace.objects.count()

    def search_workspaces(
        self, user_dict: Dict[str, Optional[Union[str, int]]], query: QueryDict
    ) -> Dict[str, Union[Dict[str, int], List[Dict[str, Union[int, List[int], str]]]]]:
        """
        search workspaces
        :param user_dict: user dictionary
        :param query: query params
        :return: paging dictionary
        """
        # get query
        query = QuerySerializer(query)

        offset = query.get('offset', 0, 'int')
        limit = query.get('limit', 10000000000, 'int')
        sort_order = query.get('sortOrder', 'asc')

        # check sort order
        helper.check_choices('sortOrder', sort_order, ['asc', 'desc'])

        # get workspace list
        workspaces = self.get_workspace_list(offset, limit, sort_order, user_dict.get('id'))
        total = self.get_workspace_total()

        return PagingSerializer(offset, limit, total, workspaces).to_dict()

    def create_new_workspace(
        self, user_dict: Dict[str, Optional[Union[str, int]]], data: Dict[str, str]
    ):
        """
        create new workspace
        :param user_dict: user dictionary
        :param data: data
        :return: created workspace
        """
        # get body data
        name = data.get('name')
        user = UserService().get_user(user_dict.get('id'))

        # check name validation
        if name is None or name == '':
            raise HttpException(400, 'Invalid workspace name')

        try:
            # create workspace and insert owner to first member
            with transaction.atomic():
                created_workspace = Workspace.objects.create(name=name, user=user)
                WorkspacesMember.objects.create(workspace=created_workspace, user=user)
        except IntegrityError:
            raise HttpException(409, name + ' already exists')

        return created_workspace

    def update_workspace(
        self,
        id: str,
        user_dict: Dict[str, Optional[Union[str, int]]],
        data: Dict[str, Union[int, List[int], str, List[Any]]],
    ) -> None:
        """
        update workspace
        :param id: workspace id
        :param user_dict: user dictionary
        :param data: data
        :return: void
        """
        # get workspace
        workspace = self.get_workspace(id)

        # get data
        member_ids = data.get('memberUserIds')
        rule_ids = data.get('ruleIds')
        project_ids = data.get('projectIds')
        name = data.get('name')

        # check owner
        if workspace.user.id != user_dict.get('id'):
            raise HttpException(403, 'Only owner can be allowed')

        # check name
        if name is not None and name == '':
            raise HttpException(400, 'Invalid name parameter')

        # check arrays
        if member_ids is not None:
            helper.check_array_item('memberUserIds', member_ids, 'int')

            # check owner in member
            if user_dict.get('id') not in member_ids:
                raise HttpException(400, 'Owner should contained in member array')

        if rule_ids is not None:
            helper.check_array_item('ruleIds', rule_ids, 'int')

        if project_ids is not None:
            helper.check_array_item('projectIds', project_ids, 'int')

        # update parameters
        workspace.name = helper.get_default_string(name, workspace.name)

        try:
            with transaction.atomic():
                # save workspace
                workspace.save()

                # delete and insert members
                self.delete_and_insert_members(workspace, member_ids)

                # delete and insert projects
                self.delete_and_insert_projects(workspace, project_ids)

                # delete and insert rules
                self.delete_and_insert_rules(workspace, rule_ids)
        except IntegrityError:
            raise HttpException(409, 'Workspace ' + workspace.name + ' already exists')

    def delete_and_insert_members(
        self, workspace: Workspace, member_ids: Optional[List[int]]
    ) -> None:
        """
        Delete and insert members
        :param workspace: workspace
        :param member_ids: member id list
        :return: void
        """
        if member_ids is not None:
            # delete members
            WorkspacesMember.objects.filter(workspace=workspace).delete()

            # add members
            for member_id in member_ids:
                self.add_members(workspace.id, member_id)

    def delete_and_insert_projects(
        self, workspace: Workspace, project_ids: Optional[List[int]]
    ) -> None:
        """
        Delete and insert projects
        :param workspace: workspace
        :param project_ids: project id list
        :return: void
        """
        if project_ids is not None:
            # delete projects
            WorkspacesProject.objects.filter(workspace=workspace).delete()

            # add projects
            for project_id in project_ids:
                self.add_projects(workspace.id, project_id)

    def delete_and_insert_rules(self, workspace: Workspace, rule_ids: Optional[List[int]]) -> None:
        """
        Delete and insert rules
        :param workspace: workspace
        :param rule_ids: rule id list
        :return: void
        """
        if rule_ids is not None:
            # delete rules
            WorkspacesRule.objects.filter(workspace=workspace).delete()

            # add rules
            for rule_id in rule_ids:
                self.add_rules(workspace.id, rule_id)

    def copy_workspace(
        self,
        id: str,
        user_dict: Dict[str, Optional[Union[str, int]]],
        data: Dict[str, str],
    ):
        """
        copy
        :param id: workspace id
        :param user_dict: user dictionary
        :param data: data
        :return: copied workspace
        """
        # get workspace
        workspace = self.get_workspace(id)

        # check member
        self.check_is_member(workspace.id, user_dict.get('id'))

        # get associates
        workspace_rules = WorkspacesRule.objects.filter(workspace=workspace)
        workspace_members = WorkspacesMember.objects.filter(workspace=workspace)
        workspace_projects = WorkspacesProject.objects.filter(workspace=workspace)

        # name
        name = data.get('name')

        # check name
        if name is None or name == '':
            raise HttpException(400, 'Invalid name parameter')

        try:
            with transaction.atomic():
                # copied workspace
                copied_workspace = self.create_new_workspace(user_dict, {'name': name})

                # add members
                for workspace_member in list(workspace_members):
                    self.add_members(copied_workspace.id, workspace_member.user.id)

                # add rules
                for workspace_rule in list(workspace_rules):
                    self.add_rules(copied_workspace.id, workspace_rule.rule.id)

                # add projects
                for workspace_project in list(workspace_projects):
                    self.add_projects(copied_workspace.id, workspace_project.project.id)
        except IntegrityError:
            raise HttpException(409, 'Workspace already exists')

        return copied_workspace

    def check_is_member(self, workspace_id: str, user_id: int):
        """
        check user is member
        :param workspace_id: workspace id
        :param user_id: user id
        :return: void
        """
        is_member = False

        workspace = self.get_workspace(workspace_id)
        workspace_members = WorkspacesMember.objects.filter(workspace=workspace)

        for workspace_member in list(workspace_members):
            if user_id == workspace_member.user.id:
                is_member = True
                break

        if not is_member:
            raise HttpException(403, 'Only workspace member can be allowed')

    def add_members(self, workspace_id: int, user_id: int) -> None:
        """
        Add members to workspace
        :param workspace_id: workspace id
        :param user_id: user id
        :return: void
        """
        # get workspace and user
        workspace = self.get_workspace(id=workspace_id)
        user = UserService().get_user(user_id)

        # get or create member
        WorkspacesMember.objects.get_or_create(workspace=workspace, user=user)

    def add_projects(self, workspace_id: int, project_id: int) -> None:
        """
        Add project to workspace
        :param workspace_id: workspace id
        :param project_id: project id
        :return: void
        """
        # get workspace and project
        workspace = self.get_workspace(id=workspace_id)
        project = ProjectService().get_project(project_id)

        # get or create project
        WorkspacesProject.objects.get_or_create(workspace=workspace, project=project)

    def add_rules(self, workspace_id: int, rule_id: int):
        """
        Add rule to workspace
        :param workspace_id: workspace id
        :param rule_id: rule id
        :return: void
        """
        # get workspace and rule
        workspace = self.get_workspace(id=workspace_id)
        rule = RuleService().get_rule(rule_id)

        # get or create rule
        WorkspacesRule.objects.get_or_create(workspace=workspace, rule=rule)
