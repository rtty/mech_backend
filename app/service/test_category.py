from typing import Dict, Optional, Union

from django.db.models.query import QuerySet
from django.http.request import QueryDict
from rest_framework import status

from app.exceptions.http import HttpException
from app.models import Test, TestCategory
from app.serializers.paging import PagingSerializer
from app.serializers.query import QuerySerializer
from app.serializers.test_category import TestCategorySerializer
from app.utils import helper


class TestCategoryService:
    """
    test categories service
    get_test_categories(); get test categories
    """

    def get_test_categories(self, category_name: Optional[str] = None) -> QuerySet:
        """
        Get total test categories
        :param category_name test category name
        :return: test categories
        """
        if category_name is not None:
            return TestCategory.objects.filter(name__icontains=category_name)
        else:
            test_categoires = TestCategory.objects.all()

            return test_categoires

    def get_test_category_with_id(self, category_id: Union[int, str]):
        """
        Get test category with id
        :param category_id: category id
        :return: test category
        """
        try:
            return TestCategory.objects.get(id=category_id)
        except TestCategory.DoesNotExist:
            raise HttpException(
                status.HTTP_404_NOT_FOUND,
                'test category with category id ' + str(category_id) + ' not exists',
            )

    def delete_category(self, query: QueryDict) -> None:
        """
        Delete test category
        :param query: query
        :return:
        """
        name = query.get('name')
        test_category = self.get_test_categories(name)

        if test_category is not None and len(test_category) > 0:
            test_category[0].delete()
        else:
            raise HttpException(
                status.HTTP_404_NOT_FOUND,
                'test category with name ' + name + ' not exists',
            )

    def create_category(self, data: Dict[str, str]) -> TestCategory:
        """
        create category
        :param data: data
        :return:
        """
        name = data.get('name')

        if name is None or name == '':
            raise HttpException(400, 'Invalid test category name')

        test_category = self.get_test_categories(name)

        if test_category is not None and len(test_category) > 0:
            raise HttpException(
                status.HTTP_409_CONFLICT,
                'test category with name ' + name + ' already exists',
            )

        return TestCategory.objects.create(name=name)

    def get_tests_category_total(self, test_category_name=None):
        """
        Get test category total count
        :return: count
        """
        if test_category_name:
            return TestCategory.objects.filter(name__icontains=test_category_name).count()
        else:
            return TestCategory.objects.count()

    def search_test_categories(
        self, query: QueryDict, with_tests: bool = False
    ) -> Dict[str, Dict[str, int]]:
        """
        search test category
        :param query: query
        :param with_tests: include tests
        :return: paging dictionary
        """
        # get queries
        query = QuerySerializer(query)

        limit = query.get('limit', 10000000000, 'int')
        offset = query.get('offset', 0, 'int')
        sort_order = query.get('sortOrder', 'asc')
        filter_name = query.get('name')

        # check sort by value
        helper.check_choices('sortOrder', sort_order, ['asc', 'desc'])

        # set desc sort by
        sort_by = 'name'
        if sort_order == 'desc':
            sort_by = '-' + sort_by

        # get test categories
        if filter_name is not None and len(filter_name):
            cats = TestCategory.objects.filter(name__icontains=filter_name).order_by(sort_by)
        else:
            cats = TestCategory.objects.order_by(sort_by)

        tests = []
        if with_tests:
            tests_by_categories = set(
                Test.objects.filter(test_category_id__in=[c.id for c in cats])
            )

            tests_by_name = set()
            if filter_name is not None and len(filter_name):
                tests_by_name = set(Test.objects.filter(name__icontains=filter_name))

            tests = sorted(
                list(tests_by_categories | tests_by_name),
                key=lambda x: x.name,
                reverse=(sort_order == 'desc'),
            )

            total = len(tests)
            tests = tests[offset * limit : offset * limit + limit]
        else:
            total = len(cats)

        category_ids = []
        results = []
        for cat in cats:
            d = TestCategorySerializer(cat).to_dict()
            if with_tests:
                d['tests'] = [
                    {'id': t.id, 'name': t.name} for t in tests if t.test_category_id == cat.id
                ]
            results.append(d)
            category_ids.append(cat.id)

        for t in tests:
            if t.test_category.id not in category_ids:
                d = TestCategorySerializer(t.test_category).to_dict()
                d['tests'] = [{'id': t.id, 'name': t.name}]
                results.append(d)
                category_ids.append(t.test_category.id)

        return PagingSerializer(offset, limit, total, results).to_dict()
