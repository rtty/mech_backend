from app.serializers.base import BaseSerializer


class TestSerializer(BaseSerializer):
    """
    tests serializer
    """

    id = 0
    name = None
    testCategoryId = 0
    testCategoryName = None

    def __init__(self, test):
        self.id = test.id
        self.name = test.name
        self.testCategoryId = test.test_category_id
        self.testCategoryName = test.test_category.name
