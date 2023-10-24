from typing import Any, List

from app.models import RuleVersionNode, RuleVersionNodeNote
from app.serializers.base import BaseSerializer
from app.serializers.rule_version_node_note import \
    RuleVersionNodeNoteSerializer


class RuleVersionNodeSerializer(BaseSerializer):
    """
    rule version node serializer
    """

    id = 0
    parentId = 0
    text = None

    def __init__(self, rule_version_node: RuleVersionNode) -> None:
        self.id = rule_version_node.node_id
        self.parentId = rule_version_node.parent_id
        self.text = rule_version_node.rule_text
        self.notes = self.get_rule_version_node_note_list(rule_version_node)

    def get_rule_version_node_note_list(self, rule_version_node: RuleVersionNode) -> List[Any]:
        """
        Get associated rule version node note list
        :param rule_version_node: rule version node
        :return: rule version node note list
        """
        results = []
        rule_version_node_notes = RuleVersionNodeNote.objects.filter(
            rule_version=rule_version_node.rule_version,
            node_id=rule_version_node.node_id,
        )

        for rule_version_node_note in list(rule_version_node_notes):
            results.append(RuleVersionNodeNoteSerializer(rule_version_node_note).to_dict())

        return results
