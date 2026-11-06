"""Validate the deliberately partial, independently derived HW2.5 profile."""
import json
from pathlib import Path


def validate(profile):
    assert profile['schema_version'] == 1
    assert profile['profile_id'] == 'ape-hw25-static'
    assert profile['hardware'] == 'HW2.5'
    assert profile['network'] is None
    assert profile['compatibility']['current_hw4'] == 'unverified'
    expected = {
        (0x3EE, 0, 37, 1), (0x3EE, 0, 38, 1),
        (0x3EE, 1, 45, 1), (0x3EE, 0, 46, 1),
        (0x399, None, 0, 4), (0x247, None, 32, 7),
        (0x5D9, 2, 46, 7),
    }
    found, names, ids = set(), set(), set()
    for message in profile['messages']:
        mid = message['message_id']
        assert 0 <= mid <= 0x7FF and mid not in ids
        ids.add(mid)
        assert message['length_bytes'] is None
        mux = message['multiplexer']
        if mux:
            assert mux == {'start_position': 0, 'width': 3 if mid == 0x3EE else 4}
        for field in message['signals']:
            start, width, page = (field[k] for k in ('start_position', 'width', 'mux_id'))
            assert width > 0 and 0 <= start < start + width <= 64
            assert field['name'] not in names
            names.add(field['name'])
            assert field['endianness'] == 'LITTLE'
            assert field['signedness'] == 'UNSIGNED'
            assert field['scale'] == 1 and field['offset'] == 0
            assert field['value_description'] == {}
            if mux:
                assert isinstance(page, int) and 0 <= page < (1 << mux['width'])
                assert start >= mux['width']
            else:
                assert page is None
            evidence = field['evidence']
            assert evidence['binary'] == ('canrx' if mid == 0x3EE else 'cantx')
            assert evidence['locations'] and evidence['verified'] and evidence['unresolved']
            key = (mid, page, start, width)
            assert key not in found
            found.add(key)
    assert found == expected
    return len(ids), len(found)


if __name__ == '__main__':
    source = Path(__file__).with_name('ape-hw25-derived.json')
    result = validate(json.loads(source.read_text()))
    print(f'PASS: {result[0]} messages, {result[1]} scoped fields; originals unchanged by this validator')
