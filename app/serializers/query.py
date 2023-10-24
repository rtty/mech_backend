from typing import Union

from django.http.request import QueryDict

from app.exceptions.http import HttpException


class QuerySerializer:
    """
    query parameter serializer
    """

    query = {}

    def __init__(self, query: QueryDict = {}) -> None:
        self.query = query

    def get(
        self, field: str, default: Union[int, str] = '', value_type: str = 'string'
    ) -> Union[int, str]:
        value = self.query.get(field)

        if value is None or value == '':
            return default
        else:
            try:
                if value_type == 'string':
                    return str(value)
                elif value_type == 'int':
                    return int(value)
                elif value_type == 'float':
                    return float(value)
                else:
                    return value
            except ValueError:
                raise HttpException(400, 'Invalid parameter type, parameter: ' + field)
