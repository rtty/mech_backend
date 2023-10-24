import json
from typing import Any, Dict

from django.http.request import QueryDict

from app.exceptions.http import HttpException
from app.parser import ParserErrors, constants
from app.parser import parse_garage_language as rule_parser
from app.parser.Node import ParserErrors as NodeErrors
from app.parser.Node import node_constants, parse_garage_node
from app.parser.Sankey.parse_to_json_tracker import get_sankey_info
from app.serializers.query import QuerySerializer
from app.serializers.rule_function import RuleFunctionSerializer
from app.utils import helper


class RuleFunctionService:
    """
    rule function service

    parse_rule_text(): parse ruleText according to function
    parse_node_text(): parse nodeText according to function
    get_test_by_category(): get specific tests with category
    """

    def __init__(self) -> None:
        """
        init parser and constants
        """
        constants.read_parser_out_file()
        node_constants.read_parser_out_file()

    def parse_node_text(self, data: Dict[str, str], function: str) -> RuleFunctionSerializer:
        node_text = data.get('nodeText')
        rule_tests = data.get('ruleTests')

        if node_text is None or (function != 'next-tokens' and node_text == ''):
            raise HttpException(400, 'nodeText does not exist')

        return self.__parse(parse_garage_node, function, node_text, rule_tests)

    def parse_rule_text(self, data: Dict[str, str], function: str):
        rule_text = data.get('ruleText')
        rule_tests = data.get('ruleTests')

        if rule_text is None or (function != 'next-tokens' and rule_text == ''):
            raise HttpException(400, 'ruleText does not exist')

        return self.__parse(rule_parser, function, rule_text, rule_tests)

    def get_test_by_category(self, query: QueryDict, function: str):
        """
        Get tests by category with a rule parser
        :param query: query
        :param function: function
        :return: dictionary
        """
        return self.__get_test_by_category(rule_parser, query, function)

    def get_node_test_by_category(self, query: QueryDict, function: str):
        """
        Get tests by category with a node parser
        :param query: query
        :param function: function
        :return: dictionary
        """
        return self.__get_test_by_category(parse_garage_node, query, function)

    def transform_for_sankey(self, data: Dict[str, Any]):
        """
        Get nodes list in Sankey format
        :param data: request data
        :return: dictionary
        """
        nodes = data.get('nodes')
        rule_text = data.get('ruleText')
        ams = data.get('ams')
        vins = data.get('vins')
        helper.check_array('nodes', nodes)
        helper.check_string('ruleText', rule_text)
        helper.check_required('ams', ams)
        helper.check_array('vins', vins)

        to_list = lambda d: {k: [v] for k, v in d.items()}

        data['vins'] = {v.get('name'): v.get('testResults') for v in vins}
        data['vinsQualifiers'] = {v.get('name'): v.get('qualifiers', '') for v in vins}

        json_nodes = get_sankey_info(data)
        nodes = json.loads(json_nodes).get('nodes')
        return RuleFunctionSerializer(nodes=nodes)

    def __get_test_by_category(self, parser, query, function):
        """
        Get rule by category for given parser
        :param parser: parser to user
        :param query: query
        :param function: function
        :return: dictionary
        """
        # get query
        query = QuerySerializer(query)

        if function == 'specific-tests':
            # get result
            return parser.get_specific_tests(query.get('category'))
        else:
            # invalid endpoint
            raise HttpException(404, 'Endpoint not found ' + function)

    def __parse(self, parser, function, text, tests):
        """
        Auxiliary function for executing given function with given parser
        :param parser: parser to use
        :param function: function to execute
        :param text: ruleText or nodeText
        :param tests: ruleTests
        """
        try:
            if function == 'next-tokens':
                # get next tokens
                tokens = parser.get_next_tokens(text or '')
                return RuleFunctionSerializer(next_tokens=tokens)

            elif function == 'translation':
                # get translation
                if tests is not None:
                    ams = self.__tests_to_mappings(tests)
                    translation = parser.get_rule(text, ams)
                else:
                    translation = parser.get_translation(text)
                return RuleFunctionSerializer(translation=translation)

            elif function == 'parses':
                # get parse state
                ams = self.__tests_to_mappings(tests) if tests is not None else (None, None, None)
                parses = parser.parses(text, ams)
                return RuleFunctionSerializer(parses=parses)

            elif function == 'is-complete':
                # get complete state
                if tests is not None:
                    ams = self.__tests_to_mappings(tests)
                    is_complete = parser.is_complete(text, ams)
                else:
                    is_complete = parser.is_complete(text)
                return RuleFunctionSerializer(is_complete=is_complete)

            else:
                # invalid endpoint
                raise HttpException(404, 'Endpoint not found ' + function)

        except (ParserErrors.IncompleteRuleError, NodeErrors.IncompleteRuleError):
            # incomplete
            raise HttpException(400, 'Rule text is incomplete')

        except (
            ParserErrors.IncorrectGrammarError,
            NodeErrors.IncorrectGrammarError,
        ):
            # incorrect
            raise HttpException(400, 'Rule text is incorrect')

    def __tests_to_mappings(self, tests):
        """
        Get mappings for parser.get_rule
        :param tests: array of objects with fields testName, testType, testCategoryName and testGroupName (optional)
        :return: ams
        """
        ams = {}
        for test in tests:
            if test['testCategoryName'] not in ams:
                ams[test['testCategoryName']] = []
            ams[test['testCategoryName']].append(test['name'])
        return ams
