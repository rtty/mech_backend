from typing import Dict, List, Union

from app.models import Project, ProjectsHasVin, Vin
from app.serializers.base import BaseSerializer
from app.serializers.vin import VinSerializer


class ProjectSerializer(BaseSerializer):
    """
    project serializer
    """

    id = 0
    name = None
    vins = []

    def __init__(self, project: Project) -> None:
        self.id = project.id
        self.name = project.name
        self.vins = self.get_vins(project)

    def get_vins(self, project: Project) -> List[Dict[str, str]]:
        """
        Get associated vins
        :param project: project
        :return: vin list
        """
        results = []
        vin_ids = []
        project_has_vins = ProjectsHasVin.objects.filter(project=project)

        for project_has_vin in list(project_has_vins):
            vin_ids.append(project_has_vin.vin_id)

        vins = Vin.objects.filter(id__in=vin_ids)

        for vin in list(vins):
            results.append(VinSerializer(vin).to_dict())

        return results
