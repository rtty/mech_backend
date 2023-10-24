from typing import Any, List, Union

from app.models import (Workspace, WorkspacesMember, WorkspacesProject,
                        WorkspacesRule)
from app.serializers.base import BaseSerializer


class WorkspaceSerializer(BaseSerializer):
    """
    workspace serializer
    """

    id = 0
    name = None
    ownerUserId = 0
    memberUserIds = []
    ruleIds = []
    projectIds = []

    def __init__(self, workspace: Workspace) -> None:
        self.id = workspace.id
        self.name = workspace.name
        self.ownerUserId = workspace.user.id
        self.memberUserIds = self.get_member_id_list(workspace)
        self.projectIds = self.get_project_id_list(workspace)
        self.ruleIds = self.get_rule_id_list(workspace)

    def get_member_id_list(self, workspace: Workspace) -> List[int]:
        """
        Get member id list
        :param workspace: workspace object
        :return: member id list
        """
        results = []
        workspace_members = WorkspacesMember.objects.filter(workspace=workspace)

        for workspace_member in list(workspace_members):
            results.append(workspace_member.user.id)

        return results

    def get_project_id_list(self, workspace: Workspace) -> List[Union[int, Any]]:
        """
        Get project id list
        :param workspace: workspace object
        :return: project id list
        """
        results = []
        workspace_projects = WorkspacesProject.objects.filter(workspace=workspace)

        for workspace_project in list(workspace_projects):
            results.append(workspace_project.project.id)

        return results

    def get_rule_id_list(self, workspace: Workspace) -> List[Any]:
        """
        Get rule id list
        :param workspace: workspace object
        :return: rule id list
        """
        results = []
        workspace_rules = WorkspacesRule.objects.filter(workspace=workspace)

        for workspace_rule in list(workspace_rules):
            results.append(workspace_rule.rule.id)

        return results
