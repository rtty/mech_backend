from typing import Any, Dict


class BaseSerializer:
    """
    base serializer
    """

    def to_dict(self) -> Dict[str, Any]:
        """
        change class to dictionary
        :return: dictionary
        """
        fields = [
            attr
            for attr in dir(self)
            if not hasattr(getattr(self, attr), '__call__') and not attr.startswith('__')
        ]

        return {field: getattr(self, field) for field in fields}
