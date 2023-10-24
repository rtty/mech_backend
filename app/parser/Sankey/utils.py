import math

test_mappings = {'A1': ['AAM[1]', 'AAM[2]'], 'key': ['key']}


def get_num_for_string(c_str):
    if c_str.endswith('NM'):
        num = -math.log10(float(c_str[:-2]) / 1000000000.0)
    elif c_str.endswith('UM'):
        num = -math.log10(float(c_str[:-2]) / 1000000.0)
    else:
        num = float(c_str)
    return num


def get_comparator(comp, num_str):
    new_comp = comp[:]
    if num_str.endswith('UM') or num_str.endswith('NM'):
        if '>' in comp:
            new_comp = comp.replace('>', '<')
        elif '<' in comp:
            new_comp = comp.replace('<', '>')
    return new_comp


def get_comparator_html(comp, num_str):
    new_comp = comp
    if num_str.endswith('UM') or num_str.endswith('NM'):
        if '>' in comp:
            new_comp = comp.replace('>', '&lt;')
        elif '<' in comp:
            new_comp = comp.replace('<', '&gt;')
    else:
        new_comp = comp.replace('>', '&gt;').replace('<', '&lt;')
    return new_comp


def chop_into_lines(msg: str) -> str:
    """
    Takes the passed in string and chops it up into multiple lines in (hopefully) an elegant way
    :param msg: the message to break up into multiple lines
    :return: a string containing the chopped up message
    """
    words = msg.split()
    chopped_up = ''
    line = ''
    for word in words:
        if len(line) < 22:
            line = f'{line} {word}'
        else:
            line = line.strip()
            if not chopped_up:
                chopped_up = line
            else:
                chopped_up = f'{chopped_up}\n{line}'
            line = word
    else:
        if line:
            line = line.strip()
            if not chopped_up:
                chopped_up = line
            else:
                chopped_up = f'{chopped_up}\n{line}'

    return chopped_up
