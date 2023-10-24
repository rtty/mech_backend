from app.models import TestCategory
from app.serializers.base import BaseSerializer


class TestCategorySerializer(BaseSerializer):
    """
    test categories
    """

    id = 0
    name = None

    def __init__(self, test_category: TestCategory) -> None:
        self.id = test_category.id
        self.name = test_category.name
