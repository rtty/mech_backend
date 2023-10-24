from typing import Any, Dict, Union

from app.models import Vin
from app.serializers.base import BaseSerializer


class VinSerializer(BaseSerializer):
    """
    vin serializer
    """

    id = 0
    vin = None
    testResults = None
    testQualifiers = None

    def __init__(self, vin: Vin, include_tests: bool = True) -> None:
        self.id = vin.id
        self.vin = vin.name

        if include_tests:
            self.testResults = self.get_test_results(vin)
            self.testQualifiers = self.get_test_qualifiers(vin) or None

    def get_test_results(self, vin: Vin) -> Dict[Any, Any]:
        """
        Get VinTests for vin
        :param vin: Vin
        :return: dictionary
        """
        return {'%s' % (x.tests.name): x.value for x in vin.vintests_set.all()}

    def get_test_qualifiers(self, vin: Vin) -> Dict[Any, Any]:
        """
        Get qualifier value for every VinTests with non-null qualifier for vin
        :param vin: Vin
        :return: dictionary
        """
        # return dict(('p%s %s test QUALIFIER' % (x.tests.type, x.tests.name), x.qualifier)
        #            for x in vin.vintests_set.filter(qualifier__isnull=False))
        return {
            '%s*qualifier' % (x.tests.name): x.qualifier
            for x in vin.vintests_set.filter(qualifier__isnull=False)
        }

    def to_dict(self) -> Dict[str, Union[int, str]]:
        result = super().to_dict()
        if self.testResults is None:
            result.pop('testResults', None)
        if self.testQualifiers is None:
            result.pop('testQualifiers', None)
        return result
