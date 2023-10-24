import os
from typing import Dict, Set

ERROR_TEXT = '__SYNTAX_ERROR__'

# List of token names.   This is always required
reserved = {
    'IF': 'IF',
    'THEN': 'THEN',
    'NO': 'NO',
    'DATA': 'DATA',
    'FOR': 'FOR',
    'ANY': 'ANY',
    'EVERY': 'EVERY',
    'OF': 'OF',
    'OTHERWISE': 'OTHERWISE',
    'THERE': 'THERE',
    'IS': 'IS',
    'CONTAINS': 'CONTAINS',
    'TEST': 'TEST',
    'VALUE': 'VALUE',
    'COMPONENT': 'COMPONENT',
    'LESS': 'LESS',
    'POWERFUL': 'POWERFUL',
    'IN': 'IN',
    'THE': 'THE',
    'CRITICAL_BREAKDOWN': 'CRITICAL_BREAKDOWN',
    'AND': 'AND',
    'OR': 'OR',
    'AT': 'AT',
    'EACH': 'EACH',
    'LEAST': 'LEAST',
    'MORE': 'MORE',
    'THAN': 'THAN',
    'FOLD': 'FOLD',
    'DIFFERENCE': 'DIFFERENCE',
    'BETWEEN': 'BETWEEN',
    'QUALIFIER': 'QUALIFIER',
    'AR': 'AR',
    'BR': 'BR',
    'CL': 'CL',
    'BL': 'BL',
    'GI': 'GI',
    'EMPTY': 'EMPTY',
}

regexp_tokens = [
    'LPAREN',
    'RPAREN',
    'COMMA',
    'MATH_OPER',
    'NUM_FOLD',
    'NUM',
    'NUMUM',
    'NUMNM',
    'COMP',
    'PRINT_VAL',
    'ID',
]

tokens = regexp_tokens + list(reserved.values())

t_COMP = r'(\<=)|(\>=)|[\<\>=]'
t_COMMA = r','
t_LPAREN = '\('
t_RPAREN = '\)'
t_MATH_OPER = '[\*\-\+\/]'
t_NUM_FOLD = r'[\-]?\d+([\.]\d+)?X'
t_NUMUM = r'[\-]?\d+([\.]\d+)?(\s)?UM'
t_NUMNM = r'[\-]?\d+([\.]\d+)?(\s)?NM'
t_NUM = r'[\-]?\d+([\.]\d+)?'

# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t\n'

### constants which should not be imported
t_PRINT_VAL = r"\"(([a-zA-Z0-9%!\:\/\,\.\-\(\)])+(\s)?)+\""
t_ID = r'[a-zA-Z_][a-zA-Z_0-9]*'

states = {}


def read_parser_out_file() -> Dict[int, Set[str]]:
    global states

    in_state = False
    num = -1
    path = os.path.join(os.path.dirname(__file__), 'parser_node.out')
    with open(path, 'r') as f:
        for line in f:
            l = line.strip()
            if len(l) > 0:
                if not in_state:
                    if l.startswith('state'):
                        w = l.split()
                        num = int(w[-1])
                        in_state = True
                        next_words = set()
                else:  # in_state is True
                    if l.startswith('state'):
                        if len(next_words) > 0:
                            states[num] = next_words
                        w = l.split()
                        num = int(w[-1])
                        in_state = True
                        next_words = set()
                    else:
                        if l.startswith('('):
                            dpos = l.find('.')
                            if dpos > -1:
                                l = l[dpos + 1 :]
                                l.strip()
                                w = l.split()
                                if len(w) > 0:
                                    if w[0] in tokens:
                                        next_words.add(w[0])
                            else:
                                if len(next_words) > 0:
                                    states[num] = next_words
                                    in_state = False
                        else:
                            w = l.split()
                            if w[0] in tokens:
                                next_words.add(w[0])
    return states


def get_allowed_tokens(state: int) -> Set[str]:
    global states
    return states[state]
