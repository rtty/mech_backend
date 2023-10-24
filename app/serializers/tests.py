from app.serializers.base import BaseSerializer


class TestsSerializer(BaseSerializer):
    """
    tests serializer
    """

    id = 0
    name = None
    type = None
    testCategoryId = 0

    def __init__(self, tests):
        self.id = tests.id
        self.name = tests.name
        self.type = tests.type
        self.testCategoryId = tests.test_categories.id
