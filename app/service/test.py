from typing import Dict, Optional, Union

from django.db import IntegrityError
from django.http.request import QueryDict
from rest_framework import status

from app.exceptions.http import HttpException
from app.models import Test
from app.serializers.paging import PagingSerializer
from app.serializers.query import QuerySerializer
from app.serializers.test import TestSerializer
from app.service.test_category import TestCategoryService
from app.utils import helper


class TestService:
    """
    get_tests(): get total tests
    """

    def get_tests(self, test_category=None):
        """
        Get total tests
        :param test_category test category dictionary
        :return: tests
        """
        if test_category is None:
            tests = Test.objects.all()
        else:
            tests = Test.objects.filter(test_category=test_category)

        results = []

        for test in list(tests):
            results.append(TestSerializer(test).to_dict())

        return results

    def get_specific_tests(self, query):
        """
        Get specific test
        :param query query
        :return:
        """
        results = {}
        category_name = query.get('name')

        if category_name is None:
            test_categories = TestCategoryService().get_test_categories()

            for test_category in list(test_categories):
                results[test_category.name] = self.get_tests(test_category)

            return results
        else:
            test_category = TestCategoryService().get_test_categories(category_name)

            if test_category is not None and len(test_category) > 0:
                return self.get_tests(test_category[0])
            else:
                raise HttpException(
                    status.HTTP_404_NOT_FOUND,
                    'test category with name ' + category_name + ' not exists',
                )

    def get_test_with_id(self, test_id: str):
        """
        Get test with id
        :param test_id: test id
        :return: test
        """
        try:
            return Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            raise HttpException(
                status.HTTP_404_NOT_FOUND,
                'test with id ' + str(test_id) + ' not exists',
            )

    def delete_specific_test(self, query: QueryDict):
        """
        Delete specific test
        :param query: query
        :return:
        """
        test_name = query.get('name')

        if test_name is None:
            raise HttpException(
                status.HTTP_400_BAD_REQUEST,
                'name parameter not exists',
            )

        try:
            Test.objects.get(name=test_name).delete()
        except Test.DoesNotExist:
            raise HttpException(
                status.HTTP_404_NOT_FOUND,
                'test name ' + test_name + ' not exists',
            )

    def add_test(self, data: Dict[str, Union[int, str]]):
        """
        Add test to test category
        :param data: data
        :return:
        """
        name = data.get('name')
        category_id = data.get('testCategoryId')

        if name is None or name == '':
            raise HttpException(400, 'Invalid test name')

        test_category = TestCategoryService().get_test_category_with_id(category_id)

        try:
            return Test.objects.create(name=name, test_category=test_category)
        except IntegrityError:
            raise HttpException(
                status.HTTP_409_CONFLICT,
                'name with ' + name + ' already exists',
            )

    def get_tests_total(self, test_name: Optional[str] = None) -> int:
        """
        Get tests total count
        :return: count
        """
        if test_name:
            return Test.objects.filter(name__icontains=test_name).count()
        else:
            return Test.objects.count()

    def search_tests(self, query: QueryDict) -> Dict[str, Dict[str, int]]:
        """
        search tests
        :param query: query
        :return: paging dictionary
        """
        # get queries
        query = QuerySerializer(query)

        limit = query.get('limit', 10000000000, 'int')
        offset = query.get('offset', 0, 'int')
        sort_by = query.get('sortBy', 'id')
        sort_order = query.get('sortOrder', 'asc')
        test_category_name = query.get('category')
        test_name = query.get('name')

        # check sort by value
        helper.check_choices('sortBy', sort_by, ['id', 'name', 'test_category_id'])
        helper.check_choices('sortOrder', sort_order, ['asc', 'desc'])

        # set desc sort by
        if sort_order == 'desc':
            sort_by = '-' + sort_by

        # get tests
        if test_name is not None and len(test_name):
            tests = Test.objects.filter(name__icontains=test_name).order_by(sort_by)[
                offset * limit : offset * limit + limit
            ]
        else:
            # get test categories
            tests = Test.objects.order_by(sort_by)[offset * limit : offset * limit + limit]

        # get total
        total = self.get_tests_total(test_name)

        results = []
        for t in tests:
            if (
                test_category_name is not None
                and len(test_category_name)
                and test_category_name not in t.test_category.name
            ):
                total = total - 1
                continue

            d = TestSerializer(t).to_dict()
            results.append(d)

        return PagingSerializer(offset, limit, total, results).to_dict()
