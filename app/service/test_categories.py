from rest_framework import status

from app.exceptions.http import HttpException
from app.models import TestCategories


class TestCategoriesService:
    """
    test categories service
    get_test_categories(); get test categories
    """

    def get_test_categories(self, category_name=None):
        """
        Get total test categories
        :param category_name test category name
        :return: test categories
        """
        if category_name is not None:
            return TestCategories.objects.filter(name=category_name)
        else:
            test_categoires = TestCategories.objects.all()

            return test_categoires

    def get_test_category_with_id(self, category_id):
        """
        Get test category with id
        :param category_id: category id
        :return: test category
        """
        try:
            return TestCategories.objects.get(id=category_id)
        except TestCategories.DoesNotExist:
            raise HttpException(
                status.HTTP_404_NOT_FOUND,
                'test category with category id ' + str(category_id) + ' not exists',
            )

    def delete_category(self, query):
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

    def create_category(self, data):
        """
        create category
        :param data: data
        :return:
        """
        name = data.get('name')
        test_category = self.get_test_categories(name)

        if test_category is not None and len(test_category) > 0:
            raise HttpException(
                status.HTTP_409_CONFLICT,
                'test category with name ' + name + ' already exists',
            )

        return TestCategories.objects.create(name=name)
