from datetime import date
from typing import Any, Dict, List, Optional, Tuple, Union

from app.models import Rule, RuleVersion
from app.serializers.base import BaseSerializer
from app.serializers.rule_version import RuleVersionSerializer


class RuleSerializer(BaseSerializer):
    """
    rule serializer
    """

    id = 0
    name = None
    ruleVersions = []

    def __init__(self, rule: Union[Tuple[Rule, bool], Rule]) -> None:
        self.id = rule.id
        self.name = rule.name
        self.ruleVersions = self.get_rule_version_list(rule)

    def get_rule_version_list(self, rule: Rule) -> List[Any]:
        """
        Get rule versions by rule object
        :param rule: rule object
        :return: rule version list
        """
      

        rule_versions = RuleVersion.objects.filter(rule=rule).order_by('version_number')

        return [
            RuleVersionSerializer(rule_version).to_dict() for rule_version in list(rule_versions)
        ]
