from typing import Any, Dict, List, Union

from django.http.request import QueryDict

from app.exceptions.http import HttpException
from app.models import Project
from app.serializers.paging import PagingSerializer
from app.serializers.project import ProjectSerializer
from app.serializers.query import QuerySerializer
from app.utils import helper


class ProjectService:
    """
    project service

    get_project(): get single project
    get_project_list(): get project list
    get_project_total(): get project total count
    search_projects(): get project pagination
    """

    def get_project(self, id: str) -> Project:
        """
        Get project
        :param id: project id
        :return: project
        """
        try:
            return Project.objects.get(id=id)
        except Project.DoesNotExist:
            raise HttpException(404, 'Project not found')

    def get_project_list(self, offset: int, limit: int, order: str, name: str) -> List[Any]:
        """
        Get project list
        :param offset: offset
        :param limit: limit
        :param order: order
        :param name: name
        :return: project list
        """
        sort_by = 'name' if order == 'asc' else '-name'

        results = []
        projects = Project.objects.filter(name__icontains=name).order_by(sort_by)[
            offset : offset + limit
        ]

        for project in list(projects):
            results.append(ProjectSerializer(project).to_dict())

        return results

    def get_project_total(self, name: str) -> int:
        """
        Get project total count
        :param name: project name
        :return: count
        """
        return Project.objects.filter(name__icontains=name).count()

    def search_projects(self, query: QueryDict) -> Dict[str, Any]:
        """
        Get project list pagination
        :param query: query
        :return: paging dictionary
        """
        # get queries
        query = QuerySerializer(query)

        name = query.get('name', '')
        offset = query.get('offset', 0, 'int')
        limit = query.get('limit', 10000000000, 'int')
        sort_order = query.get('sortOrder', 'asc')

        # check sort order
        helper.check_choices('sortOrder', sort_order, ['asc', 'desc'])

        # get project list
        project_list = self.get_project_list(offset, limit, sort_order, name)

        # get total
        total = self.get_project_total(name)

        # success
        return PagingSerializer(offset, limit, total, project_list).to_dict()
