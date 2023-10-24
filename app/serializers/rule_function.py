from typing import Dict, Optional, Set


class RuleFunctionSerializer:
    """
    rule function serializer
    """

    nextTokens = None
    translation = None
    parses = None
    isComplete = None
    nodes = None

    def __init__(
        self,
        next_tokens: Optional[Set[str]] = None,
        translation: None = None,
        parses: None = None,
        is_complete: None = None,
        nodes: None = None,
    ) -> None:
        self.nextTokens = next_tokens
        self.translation = translation
        self.parses = parses
        self.isComplete = is_complete
        self.nodes = nodes

    def to_dict(self) -> Dict[str, Set[str]]:
        """
        change class to dictionary
        :return: dictionary
        """
        Dic = {}
        fields = [
            attr
            for attr in dir(self)
            if not hasattr(getattr(self, attr), '__call__') and not attr.startswith('__')
        ]

        for field in fields:
            if getattr(self, field) is not None:
                dic[field] = getattr(self, field)

        return dic
