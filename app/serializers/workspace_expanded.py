from app.models import WorkspacesMember, WorkspacesProject, WorkspacesRule
from app.serializers.base import BaseSerializer
from app.serializers.project import ProjectSerializer
from app.serializers.rule import RuleSerializer
from app.serializers.user import UserSerializer


class WorkspaceExpandedSerializer(BaseSerializer):
    """
    workspace serializer
    """

    id = 0
    name = None
    owner = None
    members = []
    rules = []
    projects = []

    def __init__(self, workspace):
        self.id = workspace.id
        self.name = workspace.name
        self.owner = UserSerializer(workspace.user).to_dict()
        self.members = self.get_member_list(workspace)
        self.projects = self.get_project_list(workspace)
        self.rules = self.get_rule_list(workspace)

    def get_member_list(self, workspace):
        """
        Get member list
        :param workspace: workspace object
        :return: member list
        """
        results = []
        workspace_members = WorkspacesMember.objects.filter(workspace=workspace)

        for workspace_member in list(workspace_members):
            results.append(UserSerializer(workspace_member.user).to_dict())

        return results

    def get_project_list(self, workspace):
        """
        Get project list
        :param workspace: workspace object
        :return: project list
        """
        results = []
        workspace_projects = WorkspacesProject.objects.filter(workspace=workspace)

        for workspace_project in list(workspace_projects):
            results.append(ProjectSerializer(workspace_project.project).to_dict())

        return results

    def get_rule_list(self, workspace):
        """
        Get rule list
        :param workspace: workspace object
        :return: rule list
        """
        results = []
        workspace_rules = WorkspacesRule.objects.filter(workspace=workspace)

        for workspace_rule in list(workspace_rules):
            results.append(RuleSerializer(workspace_rule.rule).to_dict())

        return results
