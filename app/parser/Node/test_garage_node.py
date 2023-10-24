import node_constants
from parse_garage_node import (get_all_tokens, get_next_tokens, is_complete,
                               parses, read_test_mappings)
from ParserErrors import IncorrectGrammarError

if __name__ == '__main__':
    input_filename = '../Data/Brake_Rule_P.xlsx'  # sys.argv[1]
    text = 'IF no data for BRAKING TEST'
    text = text.upper().replace('\r', ' ').replace('\n', ' ')
    read_test_mappings(input_filename)
    print(f'parsing text: {text}')
    print('%s' % str(node_constants.read_parser_out_file()))

    print('parsing tokens')
    words = text.split()
    lenw = len(words)
    in_printval = False
    for i, word in enumerate(words):
        if not in_printval:
            if word[0] != '"':
                if i < lenw:
                    new_text = ' '.join(words[: i + 1])
                    print(f'parsing text {new_text}')
                    allowed_tokens = get_next_tokens(new_text)
                    print(f'\tallowed tokens: {allowed_tokens}')
                    if not is_complete(new_text):
                        print('incomplete or incorrect grammar')
                    else:
                        print('parses')

            else:
                in_printval = True
        else:  # in printval
            if word[-1] == '"':
                if i < lenw:
                    new_text = ' '.join(words[: i + 1])
                    print(f'parsing text in printval {new_text}')
                    get_next_tokens(new_text)
                    if not is_complete(new_text):
                        print('incomplete or incorrect grammar')
                    else:
                        print('parses')

                in_printval = False

    print('parsing full text')
    if not is_complete(text):
        print('incomplete or incorrect grammar')
    else:
        print('is complete')

    if not parses(text):
        print('invalid tokens')
    else:
        print('tokens OK')

    print('\n\n--------------\nget_all_tokens')
    print(f'{get_all_tokens()}')

    print('\n\n--------------\nget_next_tokens')
    for test_text in ('IF THERE IST', 'IF'):
        print(f'testing on: {test_text}')
        try:
            print(f'{get_next_tokens(test_text)}')
        except IncorrectGrammarError:
            print(f'Incorrect grammar: {test_text}')

    print('\n\n--------------\nis_complete')
    test_text = 'IF'
    print(f'test with incomplete but valid text: {test_text}')
    print(f'{is_complete(test_text)}\n')

    print(f'test with complete and valid text: {text}')
    print(f'{is_complete(text)}')

    print('\n\n--------------\nparses')
    test_text = 'IF THEREH IS'
    print(f'test with incorrect text: {test_text}')
    print(f'{parses(test_text)}')

    print('')
    test_text = 'IF THERE IS'
    print(f'test with correct but incomplete text: {test_text}')
    print(f'{parses(test_text)}\n')

    print('test with correct and complete text')
    print(f'{is_complete(text)}')
    print(f'Tokens\n{get_all_tokens()}')
