import json
import math
import re
import threading
from typing import Any, Dict, List, Union

import ply.lex as lex
import ply.yacc as yacc
from ply.lex import LexToken
from ply.yacc import YaccProduction

try:
    from app.parser.Sankey.constants import (ERROR_TEXT, reserved, t_COMMA,
                                             t_COMP, t_ignore, t_LPAREN,
                                             t_MATH_OPER, t_NUM, t_NUM_FOLD,
                                             t_NUMNM, t_NUMUM, t_RPAREN,
                                             tokens)
    from app.parser.Sankey.ParserErrors import (IncompleteRuleError,
                                                IncorrectGrammarError,
                                                LexError)
    from app.parser.Sankey.utils import (chop_into_lines, get_comparator,
                                         get_comparator_html,
                                         get_num_for_string)
except ModuleNotFoundError:
    from constants import ERROR_TEXT, reserved
    from ParserErrors import (IncompleteRuleError, IncorrectGrammarError,
                              LexError)

td = threading.local()


def t_ID(t: LexToken) -> LexToken:
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')  # Check for reserved words
    return t


def t_PRINT_VAL(t: LexToken) -> LexToken:
    r"\"(([_a-zA-Z0-9%\:\/\,\!\.\-\(\)])+(\s)?)+\" "
    t.value = t.value[1:-1]
    return t


# Error handling rule
def t_error(t):
    t.lexer.skip(1)
    raise LexError(t.value[0], ERROR_TEXT)


def get_message(msg: str, tok_str: str = '') -> str:
    return f'{chop_into_lines(msg)}'


def get_test_mappings(test_mappings, key, num=0):
    return test_mappings[key][num]


def get_all_test_mappings_for_key(test_mappings: Dict[str, List[str]],
                                  key: str) -> List[str]:
    return test_mappings[key]


def get_test_names_for(test_mappings: Dict[str, List[str]],
                       measurement: str) -> List[str]:
    names = []
    m = measurement + ' TEST' if not measurement.endswith(
        ' TEST') else measurement

    for j, test in enumerate((get_all_test_mappings_for_key(test_mappings,
                                                            m))):
        names.append(f'{test}')
    return names


def get_codes_for(test_mappings: Dict[str, List[str]],
                  measurement: str,
                  wrap_with: None = None) -> List[str]:
    if wrap_with is None:
        wrap_start = 'PROPERTY('
        wrap_end = ')'
    else:
        wrap_start = wrap_with + '(PROPERTY('
        wrap_end = '))'
    codes = []
    for j, test in enumerate(
            get_all_test_mappings_for_key(test_mappings, measurement)):
        codes.append(f'{test}')
    return codes


def get_test_for_absence_for_measurement(test_mappings,
                                         vin_measures,
                                         test_name,
                                         joiner='AND'):
    codes = get_codes_for(test_mappings, test_name)
    s = [f"( {test} = '')\n" for test in codes]
    return f'\n{joiner}\n'.join(s)


def get_average_for(measurement, test_mappings):
    codes = get_codes_for(test_mappings, measurement)
    s = f'({"\n".join(codes)})'
    codes = get_codes_for(test_mappings, measurement, 'ISNUMBER')
    s2 = f'({"\n".join(codes)})'
    return f'({s}\n{s2})'


def get_true_vins_for_parent(
    token_str: str,
    vin_measures: Dict[str, Dict[str, float]],
    tree_vins: Dict[str, List[List[List[Union[str, Any]]]]],
) -> List[str]:
    if token_str != 'Tok_1':
        vins = tree_vins[token_str[:-2]][-1][0]
    else:
        vins = [vin for vin in vin_measures]
    return vins


def get_false_vins_for_parent(
    token_str: str,
    vin_measures: Dict[str, Dict[str, float]],
    tree_vins: Dict[str, List[List[List[Union[str, Any]]]]],
) -> List[Union[str, Any]]:
    if token_str != 'Tok_1':
        vins = tree_vins[token_str[:-2]][-1][1]
    else:
        vins = [vin for vin in vin_measures]
    return vins


def get_vins_for_older_sibling(token_str, tree_vins):
    return tree_vins[token_str][-2][0], tree_vins[token_str][-2][1]


def get_vins_for_newer_sibling(token_str, tree_vins):
    return tree_vins[token_str][-1][0], tree_vins[token_str][-1][1]


def set_vins_for_node(
    token_str: str,
    lvins: List[Union[str, Any]],
    rvins: List[Any],
    tree_vins: Dict[str, List[List[List[Union[str, Any]]]]],
) -> None:
    if token_str not in tree_vins:
        tree_vins[token_str] = [[lvins, rvins]]
    else:
        tree_vins[token_str].append([lvins, rvins])


def get_test_averages(test_names, vins, vin_measures):
    test_averages = {}
    for vin in vins:
        sum_of_vals = 0.0
        num_of_vals = 0.0
        for test_name in test_names:
            if test_name in vin_measures[vin]:
                num_of_vals += 1
                sum_of_vals += vin_measures[vin][test_name]
        if num_of_vals > 0:
            test_averages[vin] = sum_of_vals / num_of_vals
    return test_averages


def comp_num(
    comp,
    num,
    vins,
    vin_measures,
    test_stack,
    test_mappings,
    test_name=None,
    check_every=False,
):
    lvins = []
    rvins = []
    test_names = get_test_names_for(
        test_mappings, test_stack[-1] if not test_name else test_name)

    if check_every:
        # ensure that measurements exist for each test name for each vin. Else declare the vin as false
        for vin in vins:
            for test_name in test_names:
                if test_name not in vin_measures[vin]:
                    lvins.append(vin)
                    break
            else:  # vin has all test measurements - so check for condition
                for test_name in test_names:
                    if comp == '<=':
                        if vin_measures[vin][test_name] <= num:
                            lvins.append(vin)
                        break
                    elif comp == '>=':
                        if vin_measures[vin][test_name] >= num:
                            lvins.append(vin)
                        break
                    elif comp == '<':
                        if vin_measures[vin][test_name] < num:
                            lvins.append(vin)
                        break
                    else:
                        if vin_measures[vin][test_name] > num:
                            lvins.append(vin)
                        break
                else:
                    rvins.append(vin)
    else:
        vins_to_use = vins
        test_averages = get_test_averages(test_names, vins, vin_measures)
        rvins = []
        for vin in vins_to_use:
            if comp == '<=':
                list_to_use = lvins if vin in test_averages and test_averages[
                    vin] <= num else rvins
            elif comp == '>=':
                list_to_use = lvins if vin in test_averages and test_averages[
                    vin] >= num else rvins
            elif comp == '<':
                list_to_use = lvins if vin in test_averages and test_averages[
                    vin] < num else rvins
            else:  # comp == '>':
                list_to_use = lvins if vin in test_averages and test_averages[
                    vin] > num else rvins
            list_to_use.append(vin)
    return lvins, rvins


def comp_num_between_tests(cmp_str, num, vins, test1, test2, vin_measures,
                           test_mappings):
    lvins = []
    rvins = []

    test1_names = get_test_names_for(test_mappings, test1)
    test1_averages = get_test_averages(test1_names, vins, vin_measures)

    test2_names = get_test_names_for(test_mappings, test2)
    test2_averages = get_test_averages(test2_names, vins, vin_measures)

    for vin in vins:
        use_left = False
        if cmp_str == '<':
            if vin in test1_averages and vin in test2_averages:
                if test1_averages[vin] - test2_averages[vin] < num:
                    use_left = False
                else:
                    use_left = True
        elif cmp_str == '<=':
            if vin in test1_averages and vin in test2_averages:
                if test1_averages[vin] - test2_averages[vin] <= num:
                    use_left = False
                else:
                    use_left = True
        elif cmp_str == '>=':
            if vin in test1_averages and vin in test2_averages:
                if test1_averages[vin] - test2_averages[vin] >= num:
                    use_left = False
                else:
                    use_left = True
        else:
            if vin in test1_averages and vin in test2_averages:
                if test1_averages[vin] - test2_averages[vin] > num:
                    use_left = False
                else:
                    use_left = True
        if use_left:
            lvins.append(vin)
        else:
            rvins.append(vin)
    return lvins, rvins


def p_COMPLETE_IF_THEN2(p):
    """COMPLETE_IF_THEN2 : COMPLETE_IF_THEN OTHERWISE PRINT_VAL
    | COMPLETE_IF_THEN3 OTHERWISE PRINT_VAL"""
    p.parser.tok_num[0] += '.2'
    tok_str = p.parser.tok_num[0]
    vinm = get_false_vins_for_parent(tok_str, p.parser.vin_measures,
                                     p.parser.tree_vins)
    lvins = []
    rvins = [vin for vin in set(vinm)]
    set_vins_for_node(tok_str, lvins, rvins, p.parser.tree_vins)
    p[0] = """
     %s
     {
     "text": "%s",
     "node": "%s",
     "vin_or_subvin_list": %s
     },
     """ % (
        p[1],
        get_message(p[3]).replace('\n', '\\n'),
        tok_str[4:],
        json.dumps(rvins),
    )
    p.parser.num_nodes += 1


def p_COMPLETE_IF_THEN3(p):
    """COMPLETE_IF_THEN3 : IF2_COMPARISON THEN PRINT_VAL"""
    tok_str = p.parser.tok_num[0] + '.1'
    vinm = get_true_vins_for_parent(tok_str, p.parser.vin_measures,
                                    p.parser.tree_vins)
    parent_vins = vinm + get_false_vins_for_parent(
        tok_str, p.parser.vin_measures, p.parser.tree_vins)
    parent_vins = [vin for vin in set(parent_vins)]
    rvins = []
    lvins = [vin for vin in set(vinm)]
    set_vins_for_node(tok_str, lvins, rvins, p.parser.tree_vins)
    bef_ind = p[1].rfind('}')
    if bef_ind != -1:
        p_aft = p[1][bef_ind + 1:]
        p_bef = p[1][:bef_ind + 1]
        comma = ','
    else:
        p_bef = ''
        comma = ''
        p_aft = p[1]

    p[0] = """
    %s%s
     {
     "text": "%s",
     "node": "%s",
     "vin_or_subvin_list": %s
     },
     {
     "text": "%s",
     "node": "%s",
     "vin_or_subvin_list": %s
     },
     """ % (
        p_bef,
        comma,
        p_aft.replace('\n', '\\n'),
        tok_str[4:-2],
        json.dumps(parent_vins),
        get_message(p[3]).replace('\n', '\\n'),
        tok_str[4:],
        json.dumps(lvins),
    )  # tree_vins[tok_str][-1][0])

    p.parser.num_nodes += 1


def p_COMPLETE_IF_THEN(p: YaccProduction) -> None:
    """COMPLETE_IF_THEN : IF_COMPARISON THEN PRINT_VAL"""
    tok_str = p.parser.tok_num[0] + '.1'
    vinm = get_true_vins_for_parent(tok_str, p.parser.vin_measures,
                                    p.parser.tree_vins)
    parent_vins = vinm + get_false_vins_for_parent(
        tok_str, p.parser.vin_measures, p.parser.tree_vins)
    parent_vins = [vin for vin in set(parent_vins)]
    rvins = []
    lvins = [vin for vin in set(vinm)]
    set_vins_for_node(tok_str, lvins, rvins, p.parser.tree_vins)

    p[0] = """
     {
     "text": "%s",
     "node": "%s",
     "vin_or_subvin_list": %s
     },
     {
     "text": "%s",
     "node": "%s",
     "vin_or_subvin_list": %s
     },
     """ % (
        p[1].replace('\n', '\\n'),
        tok_str[4:-2],
        json.dumps(parent_vins),
        get_message(p[3]).replace('\n', '\\n'),
        tok_str[4:],
        json.dumps(lvins),
    )  # tree_vins[tok_str][-1][0])

    p.parser.num_nodes += 1
    # unravel stack to determine which vin is left and which is right
    # set lefts


def p_IF_COMPARISON(p: YaccProduction) -> None:
    """IF_COMPARISON : IF COMPARISON"""
    p[0] = p[2]

    p.parser.stk.append(p.parser.num_nodes)
    p.parser.num_nodes += 1


# noinspection PyPep8Naming
def p_IF2_COMPARISON(p):
    """IF2_COMPARISON : IF2 COMPARISON"""
    p[0] = p[1] + p[2]

    p.parser.stk.append(p.parser.num_nodes)
    p.parser.num_nodes += 1


# noinspection PyPep8Naming
def p_COMPARISON(p: YaccProduction) -> None:
    """COMPARISON : COMPARISON1
    | COMPARISON2
    | COMPARISON3
    | COMPARISON31
    | COMPARISON4
    | COMPARISON41
    | COMPARISON5
    | COMPARISON51
    | COMPARISON52
    | COMPARISON6
    | COMPARISON61
    | COMPARISON7
    | COMPARISON711
    | COMPARISON8
    | COMPARISON9
    | COMPARISON91
    | Q_COMPARISON_IS_QUAL
    | Q_COMPARISON_IS_EVERY_QUAL
    | Q_COMPARISON_CONTAINS_EVERY_QUAL
    | Q_COMPARISON_CONTAINS_QUAL
    | Q_COMPARISON_EMPTY"""
    p[0] = p[1]


def p_COMPARISON3(p):
    """COMPARISON3 : COMPARISON AND COMPARISON
    | COMPARISON OR COMPARISON"""
    tok_str = p.parser.tok_num[0]
    lvins_0, rvins_0 = get_vins_for_older_sibling(tok_str, p.parser.tree_vins)
    lvins_1, rvins_1 = get_vins_for_newer_sibling(tok_str, p.parser.tree_vins)
    if p[2] == reserved['AND']:
        lvins = [vin for vin in lvins_0 if vin in lvins_1]
        rvins = [
            vin for vin in lvins_0 + lvins_1 + rvins_0 + rvins_1
            if vin not in lvins
        ]
    else:
        lvins = lvins_0 + lvins_1
        rvins = [vin for vin in rvins_0 + rvins_1 if vin not in lvins]

    set_vins_for_node(tok_str, lvins, rvins, p.parser.tree_vins)
    sep = '\n' if p[1].find('<SUB>') == -1 else '\n' * 2
    p[0] = f'{p[1]}{sep}{p[2]}\n{p[3]}'


def p_COMPARISON31(p):
    """COMPARISON31 : LPAREN COMPARISON AND COMPARISON RPAREN
    | LPAREN COMPARISON OR COMPARISON RPAREN"""
    tok_str = p.parser.tok_num[0]
    lvins_0, rvins_0 = get_vins_for_older_sibling(tok_str, p.parser.tree_vins)
    lvins_1, rvins_1 = get_vins_for_newer_sibling(tok_str, p.parser.tree_vins)
    if p[3] == reserved['AND']:
        lvins = [vin for vin in lvins_0 if vin in lvins_1]
        rvins = [
            vin for vin in lvins_0 + lvins_1 + rvins_0 + rvins_1
            if vin not in lvins
        ]
    else:
        lvins = lvins_0 + lvins_1
        rvins = [vin for vin in rvins_0 + rvins_1 if vin not in lvins]

    set_vins_for_node(tok_str, lvins, rvins, p.parser.tree_vins)

    sep = '\n' if p[2].find('<SUB>') == -1 else '\n' * 2
    p[0] = sep.join([f'{p[1]}{p[2]}', p[3], f'{p[4]}{p[5]}'])


def p_COMPARISON1(p: YaccProduction) -> None:
    """COMPARISON1 : THERE IS DATA FOR MEASUREMENT"""
    codes = get_codes_for(p.parser.ams, p[5])
    s = [f" NOT ({test} = '') " for test in codes]
    p[0] = f'({"\nOR\n".join(s)})'

    test_names = get_test_names_for(p.parser.ams, p[5])
    lvins = []
    rvins = []
    tok_str = p.parser.tok_num[0]
    vinm = get_false_vins_for_parent(tok_str, p.parser.vin_measures,
                                     p.parser.tree_vins)
    for vin in vinm:
        for test_name in test_names:
            if test_name in p.parser.vin_measures[vin]:
                lvins.append(vin)
                break
        else:
            rvins.append(vin)
    set_vins_for_node(tok_str, lvins, rvins, p.parser.tree_vins)


def p_COMPARISON2(p: YaccProduction) -> None:
    """COMPARISON2 : NO DATA FOR MEASUREMENT"""
    codes = get_codes_for(p.parser.ams, p[4])
    print(f'test is {p[4]}')
    print(f'tests are {codes}')
    lvins = []
    rvins = []
    tok_str = p.parser.tok_num[0]
    vinm = get_false_vins_for_parent(tok_str, p.parser.vin_measures,
                                     p.parser.tree_vins)
    test_names = get_test_names_for(p.parser.ams, p[4])
    for vin in vinm:  # for each component
        for test_name in test_names:  # for each test
            if test_name in p.parser.vin_measures[
                    vin]:  # data exists - so vin has data
                rvins.append(vin)
                break
        else:
            lvins.append(vin)

    set_vins_for_node(tok_str, lvins, rvins, p.parser.tree_vins)
    s = [f"({test} = '')\n" for test in codes]
    p[0] = f'({"\nAND\n".join(s)})'


def p_COMPARISON4(p):
    """COMPARISON4 : MEASUREMENT2 COMP NUMNM
    | MEASUREMENT2 COMP NUMUM
    | MEASUREMENT2 COMP NUM"""
    tok_str = p.parser.tok_num[0]
    vinm = get_false_vins_for_parent(tok_str, p.parser.vin_measures,
                                     p.parser.tree_vins)
    num = get_num_for_string(p[3])
    lvins, rvins = comp_num(
        get_comparator(p[2], p[3]),
        num,
        vinm,
        p.parser.vin_measures,
        p.parser.test_stack,
        p.parser.ams,
        p[1],
    )
    set_vins_for_node(tok_str, lvins, rvins, p.parser.tree_vins)
    s = get_average_for(p[1], p.parser.ams)
    num = get_num_for_string(p[3])
    p[0] = '( %s %s %f)' % (s, get_comparator_html(p[2], p[3]), num)


def p_COMPARISON41(p):
    """COMPARISON41 : MEASUREMENT2 COMP NUMUM  COMMA COMP NUMUM
    | MEASUREMENT2 COMP NUMNM  COMMA COMP NUMUM
    | MEASUREMENT2 COMP NUM  COMMA COMP NUMUM
    | MEASUREMENT2 COMP NUMUM  COMMA COMP NUMNM
    | MEASUREMENT2 COMP NUMNM  COMMA COMP NUMNM
    | MEASUREMENT2 COMP NUM  COMMA COMP NUMNM
    | MEASUREMENT2 COMP NUMUM  COMMA COMP NUM
    | MEASUREMENT2 COMP NUMNM  COMMA COMP NUM
    | MEASUREMENT2 COMP NUM  COMMA COMP NUM"""
    s = get_average_for(p[1], p.parser.ams)
    num = get_num_for_string(p[3])
    num2 = get_num_for_string(p[6])

    tok_str = p.parser.tok_num[0]
    vinm = get_false_vins_for_parent(tok_str, p.parser.vin_measures,
                                     p.parser.tree_vins)
    lvins_1, rvins = comp_num(
        get_comparator(p[2], p[3]),
        num,
        vinm,
        p.parser.vin_measures,
        p.parser.test_stack,
        p.parser.ams,
        p[1],
    )
    lvins, rvins = comp_num(
        get_comparator(p[5], p[6]),
        num2,
        lvins_1,
        p.parser.vin_measures,
        p.parser.test_stack,
        p.parser.ams,
        p[1],
    )
    rvins = [vin for vin in vinm if vin not in lvins]
    set_vins_for_node(tok_str, lvins, rvins, p.parser.tree_vins)
    p[0] = '((%s %s %f)\nAND\n(%s %s %f))' % (
        s,
        get_comparator_html(p[2], p[3]),
        num,
        s,
        get_comparator_html(p[5], p[6]),
        num2,
    )


def p_COMPARISON711(p):
    """COMPARISON711 : VALUE_FOR_ANY_TEST_OF_MEASUREMENT COMP NUMNM COMMA COMP NUMUM
    | VALUE_FOR_ANY_TEST_OF_MEASUREMENT COMP NUMNM COMMA COMP NUMNM
    | VALUE_FOR_ANY_TEST_OF_MEASUREMENT COMP NUMNM COMMA COMP NUM
    | VALUE_FOR_ANY_TEST_OF_MEASUREMENT COMP NUM COMMA COMP NUMUM
    | VALUE_FOR_ANY_TEST_OF_MEASUREMENT COMP NUM COMMA COMP NUMNM
    | VALUE_FOR_ANY_TEST_OF_MEASUREMENT COMP NUM COMMA COMP NUM
    | VALUE_FOR_ANY_TEST_OF_MEASUREMENT COMP NUMUM COMMA COMP NUMUM
    | VALUE_FOR_ANY_TEST_OF_MEASUREMENT COMP NUMUM COMMA COMP NUMNM
    | VALUE_FOR_ANY_TEST_OF_MEASUREMENT COMP NUMUM COMMA COMP NUM"""
    codes = get_codes_for(p.parser.ams, p[1])
    num = get_num_for_string(p[3])
    num2 = get_num_for_string(p[6])

    tok_str = p.parser.tok_num[0]
    vinm = get_false_vins_for_parent(tok_str, p.parser.vin_measures,
                                     p.parser.tree_vins)
    lvins_1, rvins = comp_num(
        get_comparator(p[2], p[3]),
        num,
        vinm,
        p.parser.vin_measures,
        p.parser.test_stack,
        p.parser.ams,
        p[1],
    )
    lvins, rvins = comp_num(
        get_comparator(p[5], p[6]),
        num2,
        lvins_1,
        p.parser.vin_measures,
        p.parser.test_stack,
        p.parser.ams,
        p[1],
    )
    rvins = [vin for vin in vinm if vin not in lvins]
    set_vins_for_node(tok_str, lvins, rvins, p.parser.tree_vins)

    s = [
        '((%s %s %f)\nAND\n(%s %s %f))\n' % (
            test,
            get_comparator_html(p[2], p[3]),
            num,
            test,
            get_comparator_html(p[5], p[6]),
            num2,
        ) for test in codes
    ]
    p[0] = f'({"\nOR\n".join(s)})'


def p_COMPARISON7(p):
    """COMPARISON7 : VALUE_FOR_ANY_TEST_OF_MEASUREMENT COMP NUMNM
    | VALUE_FOR_ANY_TEST_OF_MEASUREMENT COMP NUMUM
    | VALUE_FOR_ANY_TEST_OF_MEASUREMENT COMP NUM"""
    codes = get_codes_for(p.parser.ams, p[1])
    num = get_num_for_string(p[3])

    tok_str = p.parser.tok_num[0]
    vinm = get_false_vins_for_parent(tok_str, p.parser.vin_measures,
                                     p.parser.tree_vins)
    lvins, rvins = comp_num(
        get_comparator(p[2], p[3]),
        num,
        vinm,
        p.parser.vin_measures,
        p.parser.test_stack,
        p.parser.ams,
        p[1],
    )
    set_vins_for_node(tok_str, lvins, rvins, p.parser.tree_vins)

    s = [
        '( %s %s %f)\n' % (test, get_comparator_html(p[2], p[3]), num)
        for test in codes
    ]
    p[0] = f'({"\nOR\n".join(s)})'


def p_COMPARISON8(p):
    """COMPARISON8 : VALUE_FOR_EVERY_TEST_OF_MEASUREMENT COMP NUMUM
    | VALUE_FOR_EVERY_TEST_OF_MEASUREMENT COMP NUMNM
    | VALUE_FOR_EVERY_TEST_OF_MEASUREMENT COMP NUM"""
    codes = get_codes_for(p.parser.ams, p[1])
    num = get_num_for_string(p[3])
    cmp = get_comparator_html(p[2], p[3])

    tok_str = p.parser.tok_num[0]
    # false vins from previous node make it to this node. So get them
    vinm = get_false_vins_for_parent(tok_str, p.parser.vin_measures,
                                     p.parser.tree_vins)
    lvins, rvins = comp_num(
        get_comparator(p[2], p[3]),
        num,
        vinm,
        p.parser.vin_measures,
        p.parser.test_stack,
        p.parser.ams,
        p[1],
        check_every=True,
    )
    set_vins_for_node(tok_str, lvins, rvins, p.parser.tree_vins)

    s = ['(%s %s %f)\n' % (test, cmp, num) for test in codes]
    p[0] = f'({"\nAND\n".join(s)})'


def p_COMPARISON9(p):
    """COMPARISON9 : THERE IS LESS THAN NUM FOLD DIFFERENCE BETWEEN VALUE IN MEASUREMENT AND VALUE IN MEASUREMENT"""
    test1average = get_average_for(p[11], p.parser.ams)
    test2average = get_average_for(p[15], p.parser.ams)
    num = math.log10(float(p[5]))
    if num < 0:
        num = -num

    tok_str = p.parser.tok_num[0]
    vinm = get_false_vins_for_parent(tok_str, p.parser.vin_measures,
                                     p.parser.tree_vins)
    lvins, rvins = comp_num_between_tests('<', num, vinm, p[11], p[15],
                                          p.parser.vin_measures, p.parser.ams)
    set_vins_for_node(tok_str, lvins, rvins, p.parser.tree_vins)
    p[0] = '(((%s\n-\n%s) &lt; %f)\nAND\n((%s\n-\n%s) &gt; -%f))' % (
        test1average,
        test2average,
        num,
        test1average,
        test2average,
        num,
    )


def p_COMPARISON91(p):
    """COMPARISON91 : THERE IS MORE THAN NUM FOLD DIFFERENCE BETWEEN VALUE IN MEASUREMENT AND VALUE IN MEASUREMENT"""
    test1average = get_average_for(p[11], p.parser.ams)
    test2average = get_average_for(p[15], p.parser.ams)
    num = math.log10(float(p[5]))
    if num < 0:
        num = -num

    tok_str = p.parser.tok_num[0]
    vinm = get_false_vins_for_parent(tok_str, p.parser.vin_measures,
                                     p.parser.tree_vins)
    lvins, rvins = comp_num_between_tests('>', num, vinm, p[11], p[15],
                                          p.parser.vin_measures, p.parser.ams)
    set_vins_for_node(tok_str, lvins, rvins, p.parser.tree_vins)
    p[0] = '(((%s\n-\n%s) &gt; %f)\nOR\n((%s\n-\n%s) &lt; -%f))' % (
        test1average,
        test2average,
        num,
        test1average,
        test2average,
        num,
    )


def p_COMPARISON5(p):
    """COMPARISON5 : COMPONENT IS AT LEAST NUM_FOLD LESS POWERFUL IN THE MEASUREMENT"""
    # key property
    num = math.log10(float(str(p[5])[:-1]))

    tok_str = p.parser.tok_num[0]
    vinm = get_false_vins_for_parent(tok_str, p.parser.vin_measures,
                                     p.parser.tree_vins)
    lvins, rvins = comp_num_between_tests(
        '<=',
        num,
        vinm,
        p[10],
        p.parser.test_stack[-2],
        p.parser.vin_measures,
        p.parser.ams,
    )
    set_vins_for_node(tok_str, lvins, rvins, p.parser.tree_vins)

    s = '(%s\n-\n%s)' % (
        get_average_for('key test', p.parser.ams),
        get_average_for(p[10], p.parser.ams),
    )
    p[0] = '( %s &gt; %f )' % (s, num)


def p_COMPARISON51(p):
    """COMPARISON51 : VALUE FOR MEASUREMENT IS AT LEAST NUM_FOLD LESS POWERFUL THAN VALUE FOR MEASUREMENT"""
    # key property
    num = math.log10(float(str(p[7])[:-1]))

    tok_str = p.parser.tok_num[0]
    vinm = get_false_vins_for_parent(tok_str, p.parser.vin_measures,
                                     p.parser.tree_vins)
    lvins, rvins = comp_num_between_tests('<=', num, vinm, p[3], p[13],
                                          p.parser.vin_measures, p.parser.ams)
    set_vins_for_node(tok_str, lvins, rvins, p.parser.tree_vins)

    s = '( %s\n-\n%s )' % (
        get_average_for(p[13], p.parser.ams),
        get_average_for(p[3], p.parser.ams),
    )
    p[0] = '( %s &gt;= %f )' % (s, num)


def p_COMPARISON52(p):
    """COMPARISON52 : VALUE FOR MEASUREMENT IS AT LEAST NUM_FOLD MORE POWERFUL THAN VALUE FOR MEASUREMENT"""
    s = '(%s\n-\n%s)' % (
        get_average_for(p[3], p.parser.ams),
        get_average_for(p[13], p.parser.ams),
    )
    num = math.log10(float(str(p[7])[:-1]))

    tok_str = p.parser.tok_num[0]
    vinm = get_false_vins_for_parent(tok_str, p.parser.vin_measures,
                                     p.parser.tree_vins)
    lvins, rvins = comp_num_between_tests('<=', num, vinm, p[3], p[13],
                                          p.parser.vin_measures, p.parser.ams)
    set_vins_for_node(tok_str, lvins, rvins, p.parser.tree_vins)

    p[0] = '( %s &gt;= %f )' % (s, math.log10(float(str(p[7])[:-1])))


def p_COMPARISON6(p):
    """COMPARISON6 : NO DATA FOR ANY_TEST_OF_MEASUREMENT"""
    tok_str = p.parser.tok_num[0]
    lvins = []
    rvins = []
    vinm = get_false_vins_for_parent(tok_str, p.parser.vin_measures,
                                     p.parser.tree_vins)
    test_names = get_test_names_for(p.parser.ams, p[4])

    print(f'test is {p[4]}')
    print(f'tests are {test_names}')
    for vin in vinm:
        for test_name in test_names:
            if test_name not in p.parser.vin_measures[
                    vin]:  # data exists for this vin
                lvins.append(vin)
                break
        else:
            rvins.append(vin)

    set_vins_for_node(tok_str, lvins, rvins, p.parser.tree_vins)
    p[0] = get_test_for_absence_for_measurement(p.parser.ams,
                                                p.parser.vin_measures,
                                                p[4],
                                                joiner='OR')


def p_COMPARISON61(p):
    """COMPARISON61 : NO DATA FOR EVERY_TEST_OF_MEASUREMENT"""
    tok_str = p.parser.tok_num[0]
    vinm = get_false_vins_for_parent(p.parser.tok_num[0],
                                     p.parser.vin_measures, p.parser.tree_vins)

    lvins = []
    rvins = []
    test_names = get_test_names_for(p.parser.ams, p[4])

    print(f'test is {p[4]}')
    print(f'tests are {test_names}')
    for vin in vinm:
        for test_name in test_names:
            if test_name in p.parser.vin_measures[
                    vin]:  # data exists for this vin
                rvins.append(vin)
                break
        else:
            lvins.append(vin)

    set_vins_for_node(tok_str, lvins, rvins, p.parser.tree_vins)
    p[0] = get_test_for_absence_for_measurement(p.parser.ams,
                                                p.parser.vin_measures, p[4])


def p_Q_COMPARISON_CONTAINS_QUAL(p):
    """Q_COMPARISON_CONTAINS_QUAL : QUALIFIER_FOR_MEASUREMENT_CONTAINS QUAL
    | QUALIFIER_FOR_ANY_TEST_OF_MEASUREMENT_CONTAINS QUAL"""
    tok_str = p.parser.tok_num[0]

    qual = p[2]
    vins = get_false_vins_for_parent(tok_str, p.parser.vin_measures,
                                     p.parser.tree_vins)
    lvins = set()

    vin_qualifiers = p.parser.vin_qualifiers

    for vin in vins:
        if vin in vin_qualifiers:  # else it gets added to rvins later
            test_names = get_test_names_for(p.parser.ams, p[1])
            for test_name in test_names:
                if test_name in vin_qualifiers[
                        vin]:  # else it gets added to rvins later
                    qualifier = vin_qualifiers[vin][test_name]
                    # do an OR for 'AR' on any of the tests
                    if qual in qualifier:  # 'AR':
                        lvins.add(vin)

    # convert back to list from set
    lvins = [vin for vin in lvins]
    rvins = [vin for vin in vins if vin not in lvins]
    set_vins_for_node(tok_str, lvins, rvins, p.parser.tree_vins)
    p[0] = p[1]


def p_Q_COMPARISON_CONTAINS_EVERY_QUAL(p):
    """Q_COMPARISON_CONTAINS_EVERY_QUAL : QUALIFIER_FOR_EVERY_TEST_OF_MEASUREMENT_CONTAINS QUAL"""
    tok_str = p.parser.tok_num[0]

    qual = p[2]
    vins = get_false_vins_for_parent(tok_str, p.parser.vin_measures,
                                     p.parser.tree_vins)
    rvins = set()

    vin_qualifiers = p.parser.vin_qualifiers

    for vin in vins:
        if vin in vin_qualifiers:  # else it gets added to rvins later
            test_names = get_test_names_for(p.parser.ams, p[1])
            for test_name in test_names:
                if test_name in vin_qualifiers[
                        vin]:  # else it gets added to rvins later
                    qualifier = vin_qualifiers[vin][test_name]
                    # do an OR for 'AR' on any of the tests
                    if qual not in qualifier:  # 'AR':
                        rvins.add(vin)

    # convert back to list from set
    rvins = [vin for vin in rvins]
    lvins = [vin for vin in vins if vin not in rvins]
    set_vins_for_node(tok_str, lvins, rvins, p.parser.tree_vins)
    p[0] = p[1]


def p_Q_COMPARISON_IS_EVERY_QUAL(p):
    """Q_COMPARISON_IS_EVERY_QUAL : QUALIFIER_FOR_EVERY_TEST_OF_MEASUREMENT_IS QUAL"""
    tok_str = p.parser.tok_num[0]

    qual = p[2]
    vins = get_false_vins_for_parent(tok_str, p.parser.vin_measures,
                                     p.parser.tree_vins)
    rvins = set()

    vin_qualifiers = p.parser.vin_qualifiers

    for vin in vins:
        if vin in vin_qualifiers:  # else it gets added to rvins later
            test_names = get_test_names_for(p.parser.ams, p[1])
            for test_name in test_names:
                if test_name in vin_qualifiers[
                        vin]:  # else it gets added to rvins later
                    qualifier = vin_qualifiers[vin][test_name]
                    # do an OR for 'AR' on any of the tests
                    if qualifier != qual:  # 'AR':
                        rvins.add(vin)

    # convert back to list from set
    rvins = [vin for vin in rvins]
    lvins = [vin for vin in vins if vin not in rvins]
    set_vins_for_node(tok_str, lvins, rvins, p.parser.tree_vins)
    p[0] = p[1]


def p_Q_COMPARISON_IS_QUAL(p):
    """Q_COMPARISON_IS_QUAL : QUALIFIER_FOR_MEASUREMENT_IS QUAL
    | QUALIFIER_FOR_ANY_TEST_OF_MEASUREMENT_IS QUAL"""
    tok_str = p.parser.tok_num[0]

    qual = p[2]
    vins = get_false_vins_for_parent(tok_str, p.parser.vin_measures,
                                     p.parser.tree_vins)
    lvins = set()

    vin_qualifiers = p.parser.vin_qualifiers

    for vin in vins:
        if vin in vin_qualifiers:  # else it gets added to rvins later
            test_names = get_test_names_for(p.parser.ams, p[1])
            for test_name in test_names:
                if test_name in vin_qualifiers[
                        vin]:  # else it gets added to rvins later
                    qualifier = vin_qualifiers[vin][test_name]
                    # do an OR for 'AR' on any of the tests
                    if qualifier == qual:  # 'AR':
                        lvins.add(vin)

    # convert back to list from set
    lvins = [vin for vin in lvins]
    rvins = [vin for vin in vins if vin not in lvins]
    set_vins_for_node(tok_str, lvins, rvins, p.parser.tree_vins)
    p[0] = p[1]


def p_Q_COMPARISON_EMPTY(p):
    """Q_COMPARISON_EMPTY : QUALIFIER_FOR_MEASUREMENT_IS EMPTY
    | QUALIFIER_FOR_EVERY_TEST_OF_MEASUREMENT_IS EMPTY"""

    tok_str = p.parser.tok_num[0]

    vins = get_false_vins_for_parent(tok_str, p.parser.vin_measures,
                                     p.parser.tree_vins)
    rvins = set()

    vin_qualifiers = p.parser.vin_qualifiers

    for vin in vins:
        print(f'vin: {vin}')
        if vin in vin_qualifiers:  # else it gets added to lvins directly
            test_names = get_test_names_for(p.parser.ams, p[1])
            print(f'test names: {test_names}')
            for test_name in test_names:
                if test_name in vin_qualifiers[
                        vin]:  # else it gets added to lvins directly
                    qualifier = vin_qualifiers[vin][test_name]
                    print(f'qual is {qualifier}')
                    # do an AND for 'AR' on all of the tests
                    if qualifier != 'EMPTY':
                        rvins.add(vin)

    # convert back to list from set
    rvins = [vin for vin in rvins]
    lvins = [vin for vin in vins if vin not in rvins]

    set_vins_for_node(tok_str, lvins, rvins, p.parser.tree_vins)

    p[0] = p[1]


def p_VALUE_FOR_EVERY_TEST_OF_MEASUREMENT(p):
    """VALUE_FOR_EVERY_TEST_OF_MEASUREMENT : VALUE FOR EVERY_TEST_OF_MEASUREMENT IS"""
    p[0] = p[3]


def p_VALUE_FOR_ANY_TEST_OF_MEASUREMENT(p):
    """VALUE_FOR_ANY_TEST_OF_MEASUREMENT : VALUE FOR ANY_TEST_OF_MEASUREMENT IS"""
    p[0] = p[3]


def p_QUALIFIER_FOR_ANY_TEST_OF_MEASUREMENT_CONTAINS(p):
    """QUALIFIER_FOR_ANY_TEST_OF_MEASUREMENT_CONTAINS : QUALIFIER FOR ANY_TEST_OF_MEASUREMENT CONTAINS"""
    p[0] = p[3]


def p_QUALIFIER_FOR_EVERY_TEST_OF_MEASUREMENT_CONTAINS(p):
    """QUALIFIER_FOR_EVERY_TEST_OF_MEASUREMENT_CONTAINS : QUALIFIER FOR EVERY_TEST_OF_MEASUREMENT CONTAINS"""
    p[0] = p[3]


def p_QUALIFIER_FOR_ANY_TEST_OF_MEASUREMENT_IS(p):
    """QUALIFIER_FOR_ANY_TEST_OF_MEASUREMENT_IS : QUALIFIER FOR ANY_TEST_OF_MEASUREMENT IS"""
    p[0] = p[3]


def p_QUALIFIER_FOR_EVERY_TEST_OF_MEASUREMENT_IS(p):
    """QUALIFIER_FOR_EVERY_TEST_OF_MEASUREMENT_IS : QUALIFIER FOR EVERY_TEST_OF_MEASUREMENT IS"""
    p[0] = p[3]


def p_QUALIFIER_FOR_MEASUREMENT_IS(p):
    """QUALIFIER_FOR_MEASUREMENT_IS : QUALIFIER FOR MEASUREMENT IS"""
    p[0] = p[3]


def p_QUALIFIER_FOR_MEASUREMENT_CONTAINS(p):
    """QUALIFIER_FOR_MEASUREMENT_CONTAINS : QUALIFIER FOR MEASUREMENT CONTAINS"""
    p[0] = p[3]


def p_MEASUREMENT2(p):
    """MEASUREMENT2 : VALUE FOR MEASUREMENT IS"""
    p[0] = p[3]


def p_ANY_TEST_OF_MEASUREMENT(p):  # done
    """ANY_TEST_OF_MEASUREMENT : ANY OF MEASUREMENT"""
    p[0] = p[3]


def p_EVERY_TEST_OF_MEASUREMENT(p):  # done
    """EVERY_TEST_OF_MEASUREMENT : EVERY OF MEASUREMENT"""
    p[0] = p[3]


def p_MEASUREMENT(p: YaccProduction) -> None:
    """MEASUREMENT : ID TEST
    | ID CRITICAL_BREAKDOWN"""
    p[0] = f'{p[1]} {p[2]}'
    p.parser.test_stack.append(p[1])


def p_IF2(p: YaccProduction) -> None:
    """IF2 : COMPLETE_IF_THEN OTHERWISE IF
      | COMPLETE_IF_THEN3 OTHERWISE IF
    | COMPLETE_IF_THEN2 OTHERWISE IF"""
    p.parser.tok_num[0] += '.2'
    p[0] = f'{p[1]}'


def p_QUAL(p):
    """QUAL : AR
    | BR
    | CL
    | BL
    | GI"""
    p[0] = p[1]


# Error rule for syntax errors
def p_error(p: LexToken):
    if not p:
        raise IncompleteRuleError(p, ERROR_TEXT)
    else:
        raise IncorrectGrammarError(p, ERROR_TEXT)


def parse_text(
    desc: str,
    test_mappings: Dict[str, List[str]],
    vin_measures: Dict[str, Dict[str, float]],
    vin_qualifiers: Dict[str, Dict[str, str]],
):
    # Build the parser
    lexer = lex.lex()
    parser = yacc.yacc(tabmodule='r2sdot')

    parser.ams = test_mappings
    parser.tok_num = ['Tok_1']
    parser.num_nodes = 0
    parser.vin_measures = vin_measures
    parser.vin_qualifiers = vin_qualifiers
    parser.stk = []
    parser.tree_vins = {}
    parser.test_stack = []

    output = ''
    result = parser.parse(desc.upper(), debug=False)
    result = f'{{\n"nodes":[\n{re.sub(r",\s*$", "", result)}\n]\n}}'
    return result, output


def parses(rule, ams, vin_measures, vin_qualifiers):
    """
    Parses the passed in rule and returns whether or not it parses. The rule may or may not be complete.
    :param rule: the rule to parse
    :return: True if the rule parses correctly (even if incomplete). False otherwise.
    """
    try:
        parse_text(rule.upper(), ams, vin_measures, vin_qualifiers)
    except IncompleteRuleError:  # parses but is not complete
        print('Incomplete Rule')
        return True
    except IncorrectGrammarError:  # does not parse due to incorrect grammar
        print('Incorrect grammar')
        return False
    return True


def adjust_test_name(test_name: str) -> str:
    adjusted_test_name = (test_name[:-5] if test_name.endswith(' test')
                          or test_name.endswith('*test') else test_name)
    # if test_name.startswith('pValue'):
    return adjusted_test_name.strip()


def adjust_qualifier_name(test_name: str) -> str:
    elen = len(' test QUALIFIER')
    adjusted_qualifier_name = (
        test_name[:-elen] if test_name.endswith(' test QUALIFIER')
        or test_name.endswith('*test QUALIFIER') else test_name)
    # if test_name.startswith('pValue'):
    return adjusted_qualifier_name.strip()


def get_script_dot(
    text: str,
    ams: Dict[str, List[str]],
    measurements: Dict[str, Dict[str, float]],
    qualifiers: Dict[str, Union[Dict[str, str], str]],
):
    # measurements is a dictionary of the form:
    # { 'vin': {'test_name': value, 'test_name': value, ...},
    #   'vin': {...}, ...}
    vin_measures = {}  # .clear()
    vin_qualifiers = {}
    vin_qualifiers.clear()

    all_vin_names = set()
    all_test_names = set()
    for vin_name in measurements:
        all_vin_names.add(vin_name)
        vin_measures[vin_name] = {}
        vin_qualifiers[vin_name] = {}
        for test in measurements[vin_name]:
            adjusted_test_name = adjust_test_name(test)
            all_test_names.add(adjusted_test_name)
            vin_measures[vin_name][adjusted_test_name] = measurements[
                vin_name][test]
            # set qualifiers for test names to be empty by default
            vin_qualifiers[vin_name][adjusted_test_name] = 'EMPTY'

    print(f'QUALIFIERS {qualifiers}')
    for vin_name in qualifiers:
        if vin_name not in vin_qualifiers:
            vin_qualifiers[vin_name] = {}
        for test in qualifiers[vin_name]:
            if qualifiers[vin_name][test] != '':
                adjusted_qualifier_name = adjust_qualifier_name(test)
                vin_qualifiers[vin_name][adjusted_qualifier_name] = qualifiers[
                    vin_name][test]

    for vin_name in all_vin_names:
        if vin_name not in vin_qualifiers:
            vin_qualifiers[vin_name] = {}
        for test in all_test_names:
            if test not in vin_qualifiers[vin_name]:
                vin_qualifiers[vin_name][test] = 'EMPTY'

    print(f'QUALIFIERS2 {vin_qualifiers}')

    adjusted_ams = {}
    for i, key in enumerate(ams):
        adjusted_tests = []
        for test in ams[key]:
            adjusted_test_name = adjust_test_name(test)
            if len(adjusted_test_name) > 0:
                adjusted_tests.append(adjusted_test_name)
        adjusted_ams[key] = adjusted_tests
    # adjust vin_measures:
    r, output = parse_text(
        text.upper(),
        test_mappings=adjusted_ams,
        vin_measures=vin_measures,
        vin_qualifiers=vin_qualifiers,
    )
    print(f'r is {r}')
    return f'{r}'


def get_sankey_info(inps: Dict[
    str,
    Union[
        List[Dict[str, str]],
        str,
        Dict[str, List[str]],
        Dict[str, Dict[str, float]],
        Dict[str, Union[Dict[str, str], str]],
    ],
]):
    text = inps['ruleText']
    ams = inps['ams']
    measurements = inps['vins']
    qualifiers = inps['vinsQualifiers']
    return get_script_dot(text, ams, measurements, qualifiers)
