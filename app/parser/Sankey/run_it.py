from parse_to_json_tracker import get_sankey_info

json_inps = {}
json_inps[
    'ruleText'
] = """If no data for C_BRAKE TEST
THEN "missing value"
Otherwise if there is data for BRAKE_DRUM TEST
AND VALUE FOR C_BRAKE TEST is <0.25uM
AND COMPONENT is at least 24x less POWERFUL in the BRAKE_DRUM TEST 
THEN "Mode of Failure is likely to be ACCEL BRAKE CRITICAL BREAKDOWN. Check intensity"
Otherwise if there is data for DRUMCRACK TEST
AND VALUE for C_BRAKE TEST is <0.25uM
AND COMPONENT is at least 24x less POWERFUL in the BRAKEDRUM TEST 
THEN "Mode of Failure is likely to be ACCEL BRAKE. CRITICAL BREAKDOWN. Check intensity."
Otherwise if no data for BRAKE_DRUM TEST AND NO DATA FOR DRUMCRACK TEST
AND VALUE for C_BRAKE TEST is <0.25uM
THEN "Mode of Failure is possibly ACCEL BRAKE CRITICAL BREAKDOWN. Check for specific cracked drum issues."
Otherwise if there is data for BRAKE_DRUM TEST
AND VALUE for C_BRAKE TEST is <30uM
AND COMPONENT is at least 24x less POWERFUL in the BRAKE_DRUM TEST 
THEN "Mode of Failure is possibly ACCEL BRAKE CRITICAL BREAKDOWN. Check intensity."
Otherwise if there is data for DRUMCRACK TEST
AND VALUE for C_BRAKE TEST is <30uM
AND COMPONENT is at least 24x less POWERFUL in the DRUMCRACK TEST 
THEN "Mode of Failure is possibly ACCEL BRAKE CRITICAL BREAKDOWN. Check intensity."
Otherwise if VALUE for C_BRAKE TEST is <30uM
THEN "Weak ACCEL BRAKE inhibitor. Probably not the mode of failure unless driving under the inflence of alcohol."
Otherwise "unlikely to be ACCEL BRAKE mode of action."
"""
json_inps['vins'] = {
    'J456SBBJK': {
        'I.DCK/dfdf-1 test': 1.0,
        'I.ABS/garage test': 2.0,
        'I.ABS/cdo-abs test': 3.0,
        'I.CBS/c-abs test': 4.0,
        'I.CBS/cd-abs test': 5.0,
        'F.BFS/hlmi test': 6.0,
        'I.BDS/hfdf test': 3.0,
    },
    'VRTK559197': {
        'I.DCK/dfdf-1 test': 1.0,
        'I.ABS/garage test': 2.0,
        'I.ABS/cdo-abs test': 3.0,
        'I.CBS/c-abs test': 4.0,
        'I.CBS/cd-abs test': 5.0,
        'F.BFS/hlmi test': 6.0,
        'I.BDS/hfdf test': 3.0,
    },
    'VRTK559198': {
        'I.DCK/dfdf-1 test': 1.0,
        'I.ABS/garage test': 2.0,
        'I.ABS/cdo-abs test': 3.0,
        'I.CBS/c-abs test': 4.0,
        'I.CBS/cd-abs test': 5.0,
        'F.BFS/hlmi test': 6.0,
        'I.BDS/hfdf test': 3.0,
    },
    'DDWK559199': {
        'I.DCK/dfdf-1 test': 1.0,
        'I.ABS/garage test': 2.0,
        'I.ABS/cdo-abs test': 3.0,
        'I.CBS/c-abs test': 4.0,
        'I.CBS/cd-abs test': 5.0,
        'F.BFS/hlmi test': 6.0,
        'I.BDS/hfdf test': 3.0,
    },
    'DDTK559200': {
        'I.DCK/dfdf-1 test': 1.0,
        'I.ABS/garage test': 2.0,
        'I.ABS/cdo-abs test': 3.0,
        'I.CBS/c-abs test': 4.0,
        'I.CBS/cd-abs test': 5.0,
        'F.BFS/hlmi test': 6.0,
        'I.BDS/hfdf test': 3.0,
    },
    'PDDK559201': {
        'I.DCK/dfdf-1 test': 1.0,
        'I.ABS/garage test': 2.0,
        'I.ABS/cdo-abs test': 3.0,
        'I.CBS/c-abs test': 4.0,
        'I.CBS/cd-abs test': 5.0,
        'F.BFS/hlmi test': 6.0,
        'I.BDS/hfdf test': 3.0,
    },
    'PDWK559202': {
        'I.DCK/dfdf-1 test': 1.0,
        'I.ABS/garage test': 2.0,
        'I.ABS/cdo-abs test': 3.0,
        'I.CBS/c-abs test': 4.0,
        'I.CBS/cd-abs test': 5.0,
        'F.BFS/hlmi test': 6.0,
        'I.BDS/hfdf test': 3.0,
    },
}

json_inps['vinsQualifiers'] = {
    'J456SBBJK': {
        'I.DCK/dfdf-1 test QUALIFIER': 'AR',
        'I.ABS/garage test QUALIFIER': 'BR',
        'I.ABS/cdo-abs test QUALIFIER': 'BL',
        'I.CBS/c-abs test QUALIFIER': 'AR',
        'I.CBS/cd-abs test QUALIFIER': 'BR',
        'F.BFS/hlmi test QUALIFIER': 'BL',
        'I.BDS/hfdf test QUALIFIER': 'AR',
    },
    'VRTK559197': {
        'I.DCK/dfdf-1 test QUALIFIER': 'AR',
        'I.ABS/garage test QUALIFIER': 'BR',
        'I.ABS/cdo-abs test QUALIFIER': 'BL',
        'I.CBS/c-abs test QUALIFIER': 'AR',
        'I.CBS/cd-abs test QUALIFIER': 'BR',
        'F.BFS/hlmi test QUALIFIER': 'BL',
        'I.BDS/hfdf test QUALIFIER': 'AR',
    },
    'VRTK559198': {
        'I.DCK/dfdf-1 test QUALIFIER': 'AR',
        'I.ABS/garage test QUALIFIER': 'BR',
        'I.ABS/cdo-abs test QUALIFIER': 'BL',
        'I.CBS/c-abs test QUALIFIER': 'AR',
        'I.CBS/cd-abs test QUALIFIER': 'BR',
        'F.BFS/hlmi test QUALIFIER': 'BL',
        'I.BDS/hfdf test QUALIFIER': 'AR',
    },
    'DDWK559199': {
        'I.DCK/dfdf-1 test QUALIFIER': 'AR',
        'I.ABS/garage test QUALIFIER': 'BR',
        'I.ABS/cdo-abs test QUALIFIER': 'BL',
        'I.CBS/c-abs test QUALIFIER': 'AR',
        'I.CBS/cd-abs test QUALIFIER': 'BR',
        'F.BFS/hlmi test QUALIFIER': 'BL',
        'I.BDS/hfdf test QUALIFIER': 'AR',
    },
    'DDTK559200': {
        'I.DCK/dfdf-1 test QUALIFIER': 'AR',
        'I.ABS/garage test QUALIFIER': 'BR',
        'I.ABS/cdo-abs test QUALIFIER': 'BL',
        'I.CBS/c-abs test QUALIFIER': 'AR',
        'I.CBS/cd-abs test QUALIFIER': 'BR',
        'F.BFS/hlmi test QUALIFIER': 'BL',
        'I.BDS/hfdf test QUALIFIER': 'AR',
    },
    'PDDK559201': {
        'I.DCK/dfdf-1 test QUALIFIER': 'AR',
        'I.ABS/garage test QUALIFIER': 'BR',
        'I.ABS/cdo-abs test QUALIFIER': 'BL',
        'I.CBS/c-abs test QUALIFIER': 'AR',
        'I.CBS/cd-abs test QUALIFIER': 'BR',
        'F.BFS/hlmi test QUALIFIER': 'BL',
        'I.BDS/hfdf test QUALIFIER': 'AR',
    },
    'PDWK559202': {
        'I.DCK/dfdf-1 test QUALIFIER': 'AR',
        'I.ABS/garage test QUALIFIER': 'BR',
        'I.ABS/cdo-abs test QUALIFIER': 'BL',
        'I.CBS/c-abs test QUALIFIER': 'AR',
        'I.CBS/cd-abs test QUALIFIER': 'BR',
        'F.BFS/hlmi test QUALIFIER': 'BL',
        'I.BDS/hfdf test QUALIFIER': 'AR',
    },
}

json_inps['ams'] = {
    'key': ['I.Cough'],
    'key test': ['I.ABS/garage*test'],
    'C_BRAKE TEST': ['I.CBS/c-abs*test', 'I.CBS/cd-abs*test'],
    'BRAKEDRUM TEST': ['F.BFS/hlmi*test'],
    'BRAKE_DRUM TEST': ['I.BDS/hfdf*test'],
    'DRUMCRACK TEST': ['I.DCK/dfdf-1*test'],
}

if __name__ == '__main__':
    print(f'parsing text: {json_inps["ruleText"]}')
    print('Result from parsing:')

    sankey_info = get_sankey_info(json_inps)
    print(f'{sankey_info}')
