test_mappings = {'A1': ['AAM[1]', 'AAM[2]'], 'key': ['key']}


def get_message(msg):
    return "PROPERTY('" + get_test_mappings('key', 0) + "') = \"" + msg + '";\n'


def get_test_mappings(key, num=0):
    global test_mappings
    return test_mappings[key][num]
