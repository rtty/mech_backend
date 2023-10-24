from typing import Any, Dict, List, Optional, Union

from app.models import (RuleVersion, RuleVersionHasVin, RuleVersionNode,
                        RuleVersionNote, RuleVersionsHasTests, Test, Vin)
from app.serializers.base import BaseSerializer
from app.serializers.rule_version_node import RuleVersionNodeSerializer
from app.serializers.rule_version_note import RuleVersionNoteSerializer
from app.serializers.test import TestSerializer
from app.serializers.vin import VinSerializer
from app.service.test_category import TestCategoryService


class RuleVersionSerializer(BaseSerializer):
    """
    rule version serializer
    """

    id = 0
    parentRuleId = 0
    versionNumber = None
    authorUserId = 0
    authorUserName = None
    ruleTree = []
    enabledVins = []
    dateCreated = None
    dateModified = None
    state = None
    text = None
    specificTest = None
    testCategory = None
    testType = None
    notes = []
    lock = None
    tests = []

    def __init__(self, rule_version: RuleVersion) -> None:
        self.id = rule_version.id
        self.parentRuleId = rule_version.rule.id
        self.versionNumber = rule_version.version_number
        self.authorUserId = rule_version.user.id
        self.authorUserName = rule_version.user.name
        self.ruleTree = self.get_rule_version_node_list(rule_version)
        self.enabledVins = self.get_enabled_vins(rule_version)
        self.dateCreated = rule_version.date_created
        self.dateModified = rule_version.date_modified
        self.state = rule_version.state
        self.text = rule_version.text
        self.specificTest = rule_version.specific_test
        self.testType = rule_version.test_type
        self.notes = self.get_rule_version_note_list(rule_version)
        self.lock = {
            'isLocked': rule_version.is_locked,
            'lockedByUserId': rule_version.locked_by_user_id,
        }
        self.tests = self.get_rule_version_has_tests_list(rule_version)

        if len(self.tests) > 0:
            self.testCategory = (
                TestCategoryService()
                .get_test_category_with_id(
                    self.tests[0].get('testCategoryId'),
                )
                .name
            )

    def get_rule_version_node_list(
        self, rule_version: RuleVersion
    ) -> List[Dict[str, Optional[Union[int, str]]]]:
        """
        Get associated rule version node list
        :param rule_version: rule version
        :return: rule version node list
        """
        results = []
        rule_version_nodes = RuleVersionNode.objects.filter(rule_version=rule_version)

        for rule_version_node in list(rule_version_nodes):
            results.append(RuleVersionNodeSerializer(rule_version_node).to_dict())

        return results

    def get_rule_version_note_list(self, rule_version: RuleVersion) -> List[Any]:
        """
        Get associated rule version note list
        :param rule_version: rule version
        :return: rule version note list
        """
        results = []
        rule_version_notes = RuleVersionNote.objects.filter(rule_version=rule_version)

        for rule_version_note in list(rule_version_notes):
            results.append(RuleVersionNoteSerializer(rule_version_note).to_dict())

        return results

    def get_enabled_vins(self, rule_version: RuleVersion) -> List[Dict[str, Union[int, str]]]:
        """
        Get enabled vins
        :param rule_version: rule version
        :return: vin list
        """
        results = []
        vin_ids = []
        rule_version_has_vins = RuleVersionHasVin.objects.filter(rule_version=rule_version)

        for rule_version_has_vin in list(rule_version_has_vins):
            vin_ids.append(rule_version_has_vin.vins.id)

        vins = Vin.objects.prefetch_related('vintests_set', 'vintests_set__tests').filter(
            id__in=vin_ids
        )

        for vin in list(vins):
            results.append(VinSerializer(vin, include_tests=True).to_dict())

        return results

    def get_rule_version_has_tests_list(self, rule_version: RuleVersion) -> List[Any]:
        """
        Get rule versions has tests list
        :param rule_version: rule version
        :return: test list
        """
        results = []
        rule_versions_has_tests = RuleVersionsHasTests.objects.filter(rule_versions=rule_version)

        for rule_versions_has_test in list(rule_versions_has_tests):
            test = Test.objects.get(id=rule_versions_has_test.tests_id)
            results.append(TestSerializer(test).to_dict())

        return results
