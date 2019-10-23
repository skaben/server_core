from unittest import mock
from pprint import pformat
from deepdiff import DeepDiff


def pytest_assertrepr_compare(config, op, left, right):
    """Show objects' diffs in assert-equal fails using deepdiff"""

    # disable output truncation, deepdiff output can be large
    config.option.verbose = 2

    call_type = type(mock.call)

    def isiterable(obj):
        try:
            iter(obj)
            return not isinstance(obj, str)
        except TypeError:
            return False

    def is_call(obj):
        if isinstance(obj, call_type) or any(
                isinstance(item, call_type) for item in obj):
            return True

    def call_to_tuple(obj):
        if isinstance(obj, call_type):
            return tuple(obj)
        else:
            return map(tuple, obj)

    explanation = None

    try:
        if op == '==':
            if isiterable(left) and isiterable(right):
                if is_call(left) or is_call(right):
                    explanation = DeepDiff(call_to_tuple(left),
                                           call_to_tuple(right))
                else:
                    explanation = DeepDiff(left, right)

                explanation = pformat(explanation, indent=2).split('\n')
    except Exception as e:
        explanation = [
            '(deepdiff plugin: representation of details failed.  ',
            'Probably an object has a faulty __repr__.)',
            str(e)
        ]

    return explanation
