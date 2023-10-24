from django.db import IntegrityError
from rest_framework import status

from app.exceptions.http import HttpException
from app.models import Tests
from app.serializers.tests import TestsSerializer
from app.service.test_categories import TestCategoriesService


class TestsService:
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
            tests = Tests.objects.all()
        else:
            tests = Tests.objects.filter(test_categories=test_category)

        results = []

        for test in list(tests):
            results.append(TestsSerializer(test).to_dict())

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
            test_categories = TestCategoriesService().get_test_categories()

            for test_category in list(test_categories):
                results[test_category.name] = self.get_tests(test_category)

            return results
        else:
            test_category = TestCategoriesService().get_test_categories(category_name)

            if test_category is not None and len(test_category) > 0:
                return self.get_tests(test_category[0])
            else:
                raise HttpException(
                    status.HTTP_404_NOT_FOUND,
                    'test category with name ' + category_name + ' not exists',
                )

    def delete_specific_test(self, query):
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
            Tests.objects.get(name=test_name).delete()
        except Tests.DoesNotExist:
            raise HttpException(
                status.HTTP_404_NOT_FOUND,
                'test name ' + test_name + ' not exists',
            )

    def add_test(self, data):
        """
        Add test to test category
        :param data: data
        :return:
        """
        name = data.get('name')
        category_id = data.get('testCategoryId')
        test_category = TestCategoriesService().get_test_category_with_id(category_id)

        try:
            return Tests.objects.create(name=name, test_categories=test_category)
        except IntegrityError:
            raise HttpException(
                status.HTTP_409_CONFLICT,
                'name with ' + name + ' already exists',
            )
