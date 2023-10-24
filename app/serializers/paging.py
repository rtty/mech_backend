from typing import Any, List

from app.serializers.base import BaseSerializer


class PagingSerializer(BaseSerializer):
    """
    paging serializer
    """

    results = []
    paginationInfo = {
        'limit': 0,
        'offset': 0,
        'totalCount': 0,
    }

    def __init__(
        self, offset: int = 0, limit: int = 0, total: int = 0, data: List[Any] = []
    ) -> None:
        self.paginationInfo['offset'] = offset
        self.paginationInfo['limit'] = limit
        self.paginationInfo['totalCount'] = total
        self.results = data
