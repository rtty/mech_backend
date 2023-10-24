import io
import math
from contextlib import redirect_stderr
from typing import Optional, Tuple

import pandas as pd
import ply.lex as lex
import ply.yacc as yacc
from ply.yacc import LRParser

import app.parser.constants as constants
from app.parser.constants import ERROR_TEXT, reserved
from app.parser.ParserErrors import (IncompleteRuleError,
                                     IncorrectGrammarError, LexError)


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')  # Check for reserved words
    return t


def t_PRINT_VAL(t):
    r"\"(([_a-zA-Z0-9%\:\/\,\!\.\-\(\)])+(\s)?)+\" "
    t.value = t.value[1:-1]
    return t


# Error handling rule
def t_error(t):
    t.lexer.skip(1)
    raise LexError(t.value[0], ERROR_TEXT)


def get_message(msg):
    return "return '" + msg + "'"


def get_test_mappings(test_mappings, key, num=0):
    if key != 'key' or 'key' in test_mappings:
        tms = test_mappings[key][num]
    else:
        tms = 'new_function'
    return tms


def get_all_test_mappings_for_key(test_mappings, key):
    return test_mappings[key]


def set_all_test_names_for(measurement, test_mappings, defns):
    codes = []
    for test in get_all_test_mappings_for_key(test_mappings, measurement):
        codes.append(f"'{test}'")
    defns[measurement] = codes


def get_codes_for(test_mappings, measurement, wrap_with=None):
    if wrap_with is None:
        wrap_start = 'PROPERTY('
        wrap_end = ')'
    else:
        wrap_start = wrap_with + '(PROPERTY('
        wrap_end = '))'
    codes = []
    for j, test in enumerate(get_all_test_mappings_for_key(test_mappings, measurement)):
        codes.append(f"{wrap_start}'{test}'{wrap_end}")
    return codes


def get_test_for_absence_for_measurement(test_mappings, test_name, joiner=' and '):
    codes = get_codes_for(test_mappings, test_name)
    s = [f'math.isnan("{test}")' for test in codes]
    return f' {joiner} '.join(s)


def get_comparator(comp, num_str):
    new_comp = comp
    if num_str.endswith('UM') or num_str.endswith('NM'):
        if '>' in comp:
            new_comp = comp.replace('>', '<')
        elif '<' in comp:
            new_comp = comp.replace('<', '>')
    return new_comp


def get_num_for_string(c_str):
    if c_str.endswith('NM'):
        num = -math.log10(float(c_str[:-2]) / 1000000000.0)
    elif c_str.endswith('UM'):
        num = -math.log10(float(c_str[:-2]) / 1000000.0)
    else:
        num = float(c_str)
    return num


def format_to_lines(s):
    members = s[1:-1].replace('],', '],\n        ')
    return f'{{\n         {members}\n        }}'


def get_lib_functions(defns):
    return """
# Definitions
defns = %s

def data_value(test_name, props):
    return props.get(test_name).getValue().getFloat()
    

def has_data(indiv_test_name, props):
    return not math.isnan(data_value(indiv_test_name, props))


def was_measured(measurement, props):
    codes = defns[measurement]
    for test in codes:
        if has_data(test, props):
            return True
    else:
        return False


def get_average(measurement, props):
    codes = defns[measurement]
    s = [data_value(test, props) for test in codes if has_data(test, props)]
    return sum(s)/len(s)


def compare_any_of(measurement, cmp, num, props):
    codes = defns[measurement]
    for test in codes:
        if has_data(test, props):
            if cmp == '<':
                if data_value(test, props) < num:
                    return True
            elif cmp == '>':
                if data_value(test, props) > num:
                    return True
            elif cmp == '>=':
                if data_value(test, props) >= num:
                    return True
            else: 
                if data_value(test, props) <= num:
                    return True
    return False


def compare_every_of(measurement, cmp, num, props):
    codes = defns[measurement]
    for test in codes:
        if has_data(test, props):
            if cmp == '<':
                if data_value(test, props) >= num:
                    return False
            elif cmp == '>':
                if data_value(test, props) <= num:
                    return False
            elif cmp == '>=':
                if data_value(test, props) < num:
                    return False
            else: 
                if data_value(test, props) > num:
                    return False
        else:
            return False
    return True
    
    
""" % format_to_lines(
        str(defns).replace("\"'", "'").replace("'\"", "'")
    )


def p_COMPLETE_IF_THEN2(p):
    """COMPLETE_IF_THEN2 : COMPLETE_IF_THEN OTHERWISE PRINT_VAL"""
    p[
        0
    ] = """
%s
def %s(props):
    %s
    else:
        %s
""" % (
        get_lib_functions(p.parser.defns),
        get_test_mappings(p.parser.test_mappings, 'key', 0).replace('.', '_dot_'),
        p[1],
        get_message(p[3]),
    )


def p_COMPLETE_IF_THEN(p):
    """COMPLETE_IF_THEN : IF_COMPARISON THEN PRINT_VAL
    | IF_COMPARISON2 THEN PRINT_VAL"""
    p[
        0
    ] = f"""{p[1]}:
        {get_message(p[3])}
"""


def p_IF_COMPARISON(p):
    """IF_COMPARISON : IF COMPARISON"""
    p[0] = f'if {(p[2].strip())}'


def p_IF_COMPARISON2(p):
    """IF_COMPARISON2 : IF2 COMPARISON"""
    p[0] = f'{p[1]} {p[2].strip()}'


def p_COMPARISON(p):
    """COMPARISON : COMPARISON1
    | COMPARISON2
    | COMPARISON301
    | COMPARISON302
    | COMPARISON311
    | COMPARISON312
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
    | Q_COMPARISON_IS_EMPTY
    | Q_COMPARISON_CONTAINS_QUAL"""
    p[0] = p[1]


def p_COMPARISON301(p):
    """COMPARISON301 : COMPARISON AND COMPARISON"""
    p[0] = ' and '.join([p[1], p[3]])


def p_COMPARISON302(p):
    """COMPARISON302 : COMPARISON OR COMPARISON"""
    p[0] = ' or '.join([p[1], p[3]])


def p_COMPARISON311(p):
    """COMPARISON311 : LPAREN COMPARISON AND COMPARISON RPAREN"""
    p[0] = ' and '.join([f'{p[1]}({p[2]})', f'({p[4]}){p[5]}'])


def p_COMPARISON312(p):
    """COMPARISON312 : LPAREN COMPARISON OR COMPARISON RPAREN"""
    p[0] = ' or '.join([f'{p[1]}({p[2]})', f'({p[4]}){p[5]}'])


def p_COMPARISON1(p):
    """COMPARISON1 : THERE IS DATA FOR MEASUREMENT"""
    set_all_test_names_for(p[5], p.parser.test_mappings, p.parser.defns)
    s = f'was_measured("{p[5]}", props)'
    p[0] = s


def p_COMPARISON2(p):
    """COMPARISON2 : NO DATA FOR MEASUREMENT"""
    set_all_test_names_for(p[4], p.parser.test_mappings, p.parser.defns)
    s = f'(not was_measured("{p[4]}", props))'  # str(codes)
    p[0] = s


def p_COMPARISON4(p):
    """COMPARISON4 : MEASUREMENT2 COMP NUMUM
    | MEASUREMENT2 COMP NUMNM
    | MEASUREMENT2 COMP NUM"""
    num = get_num_for_string(p[3])
    set_all_test_names_for(p[1], p.parser.test_mappings, p.parser.defns)
    p[0] = '( get_average(%s, props) %s %f )' % (p[1], get_comparator(p[2], p[3]), num)


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
    num = get_num_for_string(p[3])
    num2 = get_num_for_string(p[6])
    set_all_test_names_for(p[1], p.parser.test_mappings, p.parser.defns)
    p[0] = '((get_average(%s, props) %s %f) and (get_average(%s, props) %s %f)) ' % (
        p[1],
        get_comparator(p[2], p[3]),
        num,
        p[1],
        get_comparator(p[5], p[6]),
        num2,
    )


def p_COMPARISON711(p):
    """COMPARISON711 : VALUE_FOR_ANY_OF_MEASUREMENT COMP NUMNM COMMA COMP NUMUM
    | VALUE_FOR_ANY_OF_MEASUREMENT COMP NUMNM COMMA COMP NUMNM
    | VALUE_FOR_ANY_OF_MEASUREMENT COMP NUMNM COMMA COMP NUM
    | VALUE_FOR_ANY_OF_MEASUREMENT COMP NUM COMMA COMP NUMUM
    | VALUE_FOR_ANY_OF_MEASUREMENT COMP NUM COMMA COMP NUMNM
    | VALUE_FOR_ANY_OF_MEASUREMENT COMP NUM COMMA COMP NUM
    | VALUE_FOR_ANY_OF_MEASUREMENT COMP NUMUM COMMA COMP NUMUM
    | VALUE_FOR_ANY_OF_MEASUREMENT COMP NUMUM COMMA COMP NUMNM
    | VALUE_FOR_ANY_OF_MEASUREMENT COMP NUMUM COMMA COMP NUM"""
    num1 = get_num_for_string(p[3])
    num2 = get_num_for_string(p[6])
    cmp1 = get_comparator(p[2], p[3])
    cmp2 = get_comparator(p[5], p[6])
    p[0] = "compare_any_of('%s', '%s', %f, props)" % (p[1], cmp1, num1)
    p[0] = "%s and compare_any_of('%s', '%s', %f, props)" % (p[0], p[1], cmp2, num2)


def p_COMPARISON7(p):
    """COMPARISON7 : VALUE_FOR_ANY_OF_MEASUREMENT COMP NUMNM
    | VALUE_FOR_ANY_OF_MEASUREMENT COMP NUMUM
    | VALUE_FOR_ANY_OF_MEASUREMENT COMP NUM"""
    num = get_num_for_string(p[3])
    cmp = get_comparator(p[2], p[3])
    p[0] = "compare_any_of('%s', '%s', %f, props)" % (p[1], cmp, num)


def p_COMPARISON8(p):
    """COMPARISON8 : VALUE_FOR_EVERY_OF_MEASUREMENT COMP NUMUM
    | VALUE_FOR_EVERY_OF_MEASUREMENT COMP NUMNM
    | VALUE_FOR_EVERY_OF_MEASUREMENT COMP NUM"""
    num = get_num_for_string(p[3])
    cmp = get_comparator(p[2], p[3])
    p[0] = "compare_every_of('%s', '%s', %f, props)" % (p[1], cmp, num)


def p_COMPARISON9(p):
    """COMPARISON9 : THERE IS LESS THAN NUM FOLD DIFFERENCE BETWEEN VALUE IN MEASUREMENT AND VALUE IN MEASUREMENT"""
    num = math.log10(float(p[5]))
    if num < 0:
        num = -num
    set_all_test_names_for(p[11], p.parser.test_mappings, p.parser.defns)
    set_all_test_names_for(p[15], p.parser.test_mappings, p.parser.defns)
    p[0] = (
        '(((get_average(%s) - get_average(%s, props)) < %f) and ((get_average(%s, props) - get_average(%s, props)) > -%f))'
        % (p[11], p[15], num, p[11], p[15], num)
    )


def p_COMPARISON91(p):
    """COMPARISON91 : THERE IS MORE THAN NUM FOLD DIFFERENCE BETWEEN VALUE IN MEASUREMENT AND VALUE IN MEASUREMENT"""
    num = math.log10(float(p[5]))
    if num < 0:
        num = -num
    set_all_test_names_for(p[11], p.parser.test_mappings, p.parser.defns)
    set_all_test_names_for(p[15], p.parser.test_mappings, p.parser.defns)
    p[0] = (
        '(((get_average(%s, props) - get_average(%s, props)) > %f) or ((get_average(%s, props) - get_average(%s, props)) < -%f))'
        % (p[11], p[15], num, p[11], p[15], num)
    )


def p_COMPARISON5(p):
    """COMPARISON5 : COMPONENT IS AT LEAST NUM_FOLD LESS POWERFUL IN THE MEASUREMENT"""
    # key property
    set_all_test_names_for('key test', p.parser.test_mappings, p.parser.defns)
    set_all_test_names_for(p[10], p.parser.test_mappings, p.parser.defns)
    s = f'(get_average("key test", props) - get_average({p[10]}, props))'
    p[0] = '( %s > %f )' % (s, math.log10(float(str(p[5])[:-1])))


def p_COMPARISON51(p):
    """COMPARISON51 : VALUE FOR MEASUREMENT IS AT LEAST NUM_FOLD LESS POWERFUL THAN VALUE FOR MEASUREMENT"""
    # key property
    set_all_test_names_for(p[13], p.parser.test_mappings, p.parser.defns)
    set_all_test_names_for(p[3], p.parser.test_mappings, p.parser.defns)

    s = f'( get_average({p[13]}, props) - get_average({p[3]}, props) )'
    p[0] = '( %s >= %f )' % (s, math.log10(float(str(p[7])[:-1])))


def p_COMPARISON52(p):
    """COMPARISON52 : VALUE FOR MEASUREMENT IS AT LEAST NUM_FOLD MORE POWERFUL THAN VALUE FOR MEASUREMENT"""
    # key property
    set_all_test_names_for(p[3], p.parser.test_mappings, p.parser.defns)
    set_all_test_names_for(p[13], p.parser.test_mappings, p.parser.defns)

    s = f'(get_average({p[3]}, props) - get_average({p[13]}, props))'
    p[0] = '( %s >= %f )' % (s, math.log10(float(str(p[7])[:-1])))


def p_COMPARISON6(p):
    """COMPARISON6 : NO DATA FOR ANY_OF_MEASUREMENT"""
    p[0] = get_test_for_absence_for_measurement(p.parser.test_mappings, p[4], joiner='OR')


def p_COMPARISON61(p):
    """COMPARISON61 : NO DATA FOR EVERY_OF_MEASUREMENT"""
    p[0] = f'not was_measured("{p[4]}", props)'


def get_qualifier_in_code_to(test_name, qualifier, test_mappings):
    test_names = get_all_test_mappings_for_key(test_mappings, test_name)
    s = [f'( "{qualifier}" in get_qualifier("{test_name}", props)) ' for test_name in test_names]
    return f'({" and ".join(s)})'


def p_Q_COMPARISON_CONTAINS_QUAL(p):
    """Q_COMPARISON_CONTAINS_QUAL : QUALIFIER_FOR_MEASUREMENT_CONTAINS QUAL"""
    test_name = p[1]
    p[0] = get_qualifier_in_code_to(test_name, p[2], p.parser.test_mappings)


def get_qualifier_comparison_code_to(test_nameA, qualifier, test_mappings):
    test_names = get_all_test_mappings_for_key(test_mappings, test_nameA)
    s = [f'( "{qualifier}" == get_qualifier("{test_name}", props)) ' for test_name in test_names]
    return f'({" and ".join(s)})'


def p_Q_COMPARISON_IS_QUAL(p):
    """Q_COMPARISON_IS_QUAL : QUALIFIER_FOR_MEASUREMENT_IS QUAL"""
    test_name = p[1]
    p[0] = get_qualifier_comparison_code_to(test_name, p[2], p.parser.test_mappings)


def p_Q_COMPARISON_IS_EMPTY(p):
    """Q_COMPARISON_IS_EMPTY : QUALIFIER_FOR_MEASUREMENT_IS EMPTY"""
    test_name = p[1]
    p[0] = get_qualifier_comparison_code_to(test_name, '', p.parser.test_mappings)


def p_VALUE_FOR_EVERY_OF_MEASUREMENT(p):
    """VALUE_FOR_EVERY_OF_MEASUREMENT : VALUE FOR EVERY_OF_MEASUREMENT IS"""
    p[0] = p[3]


def p_VALUE_FOR_ANY_OF_MEASUREMENT(p):
    """VALUE_FOR_ANY_OF_MEASUREMENT : VALUE FOR ANY_OF_MEASUREMENT IS"""
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


def p_ANY_OF_MEASUREMENT(p):
    """ANY_OF_MEASUREMENT : ANY OF MEASUREMENT"""
    p[0] = p[3]


def p_EVERY_OF_MEASUREMENT(p):
    """EVERY_OF_MEASUREMENT : EVERY OF MEASUREMENT"""
    p[0] = p[3]


def p_MEASUREMENT(p):
    """MEASUREMENT : ID TEST
    | ID CRITICAL_BREAKDOWN"""
    p[0] = f'{p[1]} {p[2]}'


def p_IF2(p):
    """IF2 : COMPLETE_IF_THEN OTHERWISE IF"""
    p[0] = f'{p[1]}\n    elif '


def p_QUAL(p):
    """QUAL : AR
    | BR
    | CL
    | BL
    | GI"""
    p[0] = p[1]


# Error rule for syntax errors
def p_error(p):
    if not p:
        raise IncompleteRuleError(p, ERROR_TEXT)
    else:
        raise IncorrectGrammarError(p, ERROR_TEXT)


def get_lexer():
    """
    Build lexer
    """
    return lex.lex()


def set_mappings(p: LRParser, ams: Optional[Tuple[None, None, None]]) -> None:
    if ams is not None:
        p.test_mappings = ams
        p.defns = {}


def parse_text(desc: str, ams: Optional[Tuple[None, None, None]] = None):
    # Build the parser
    lexer = lex.lex()
    parser = yacc.yacc()
    set_mappings(parser, ams)

    output = ''
    print('in parse_text(desc)')
    debug_print(parser=parser)
    result = parser.parse(desc.upper(), debug=False)
    return result, output


def get_translation(desc: str):
    """
    Translates the provided text in desc to the desired script language
    :param desc: the text to be translated
    :return: the translated text
    :raise IncompleteGrammarError if the grammar is incorrect
    :raise IncompleteRuleError if the rule parses but is not complete
    """
    print('in get_translation')
    result, output = parse_text(desc)
    return result


def get_next_tokens(desc, ams):
    """
    Returns a set containing the next set of allowed tokens after the last token in the provided
    text. The text must conform to the rules and grammar required.
    :param desc: the provided completed or semi-completed rule
    :return: a set containing the set of the next allowed tokens after the last word in the rule.
    If the rule is complete, returns an empty set.
    :raise IncorrectGrammarError if the rule passed in has incorrect grammar
    """
    # Build the parser
    lexer = lex.lex()
    parser = yacc.yacc()
    set_mappings(parser, ams)
    state_num = -1
    complete = False
    with io.StringIO() as buf, redirect_stderr(buf):
        try:
            parser.parse(desc.upper(), debug=True)
            complete = True
        except IncompleteRuleError:
            output = buf.getvalue()
            lines = output.split('\n')
            state_num = -1
            for line in lines:
                if line.startswith('State  :'):
                    w = line.split()
                    state_num = int(w[-1])
    return {} if complete else constants.get_allowed_tokens(state_num)


# def get_rule_text(fname='Data/TestMappings.xlsx'):
#     for i in range(len(df)):
#         if line_text != '' and line_text != 'nan':
#             if len(rule_text) > 0:


def get_all_tokens():
    """
    Returns a dictionary of all the allowed tokens with the token names as keys and the regular expressions
    corresponding to each token as values
    :return: a dictionary of all the allowed tokens with the token names as keys and the regular expressions
    corresponding to each token as values
    """
    all_tokens = {}
    for key in reserved:
        all_tokens[key] = reserved[key]
    for token in constants.regexp_tokens:
        all_tokens[token] = getattr(constants, f't_{token}')
    return all_tokens


def is_complete(rule, ams):
    """
    Returns whether or not the passed in rule is complete
    :param rule: the rule to parse
    :param ams: test mappings
    :return: True if the rule is valid and complete. False otherwise
    """
    try:
        parse_text(rule.upper(), ams)
    except IncompleteRuleError:
        print(f'Incomplete Rule: {rule}')
        return False
    except IncorrectGrammarError:
        print('incorrect grammar')
        return False
    return True


def parses(rule: str, ams: Tuple[None, None, None]):
    """
    Parses the passed in rule and returns whether or not it parses. The rule may or may not be complete.
    :param rule: the rule to parse
    :param ams: test mappings
    :return: True if the rule parses correctly (even if incomplete). False otherwise.
    """
    try:
        parse_text(rule.upper(), ams)
    except IncompleteRuleError:  # parses but is not complete
        print('Incomplete Rule')
        return True
    except IncorrectGrammarError:  # does not parse due to incorrect grammar
        print('Incorrect grammar')
        return False
    return True


def read_test_mappings(input_excelfile='Data/TestMappings.xlsx'):
    import inspect

    print(f'called from {inspect.stack()[1][3]}')
    df = pd.read_excel(input_excelfile, sheet_name='Mappings')
    df.dropna()
    td_test_mappings = {}

    current_ac = None  # test category or enzyme name
    for i in range(len(df)):
        ac = df.loc[i, 'Test Category']
        if pd.notna(ac):
            ac = ac.strip()
        if pd.notna(ac) and len(ac) > 0:
            current_ac = ac
        # else current_ac is the previous ac name
        test = df.loc[i, 'Test']
        if pd.notna(test):
            test = test.strip()
            if current_ac not in td_test_mappings:
                td_test_mappings[current_ac] = []
            td_test_mappings[current_ac].append(test)

    return td_test_mappings


def debug_print(parser: LRParser):
    print('**************************')
    print(f'parser.test_mappings {parser.test_mappings}')
    print('**************************')


def get_rule(text, ams):
    global td_test_mappings
    td_test_mappings = {}
    print('in parse_garage_language.get_rule() before')
    for from_d, to_d in zip([ams], [td_test_mappings]):
        if from_d != to_d:
            to_d.clear()
            for k in from_d:
                to_d[k] = from_d[k]
    print('in parse_garage_language.get_rule() after')
    r, output = parse_text(text.upper(), ams)
    return r


def get_specific_tests(test_category: str):
    """
    If test_category is specified, returns a set of the specific tests for the test_category, if
    the test_category is valid. Returns None if the test_category is not valid.
    If test_category is not specified, returns a dictionary containing all test_category names
    as keys with a set containing the specific tests for that test category as values.
    :param test_category: the name of the test category for which the specific tests are needed.
    :return: None if the test_category is not valid. A
    Returns a list of strings for the provided token which are in the token map. A set of the specific tests for the
    test_category, if
    the test_category is valid. A dictionary containing all test_category names
    as keys with a set containing the specific tests for that test category as values, if test_category is None.
    """
    if not test_category:
        return td_test_mappings
    elif test_category in td_test_mappings:
        return td_test_mappings[test_category]
    else:
        return None
