from collections.abc import Callable
from typing import List, Optional
import operator
import logging
import re

from .trx import TestData

OPERATOR_MAP = {
    "==": operator.eq,
    "!=": operator.ne,
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge
}

CONDITION_PATTERN = re.compile(fr"^\s*(\w+)\s*({'|'.join(OPERATOR_MAP.keys())})\s*(\S+)\s*$")

def split_word(string: str, word: str) -> List[str]:
    return re.split(fr"(?:^|(?<=\s)){re.escape(word)}(?:$|(?=\s))", string)

def get_operator(op: str):
    if op == "==":
        return operator.eq
    elif op == "!=":
        return operator.ne
    elif op == "<":
        return operator.lt
    elif op == "<=":
        return operator.le
    elif op == ">":
        return operator.gt
    elif op == ">=":
        return operator.ge
    else:
        raise RuntimeError()

def build_filter(filter_str: str) -> Optional[Callable[[TestData], bool]]:
    or_methods = []
    for and_chain in split_word(filter_str, "or"):
        and_methods = []
        for condition in split_word(and_chain, "and"):
            try:
                attr_str, op_str, rvalue_str = CONDITION_PATTERN.match(condition).groups()
                op = get_operator(op_str)

                # The default arguments necessetiate Python to capture by value.
                def constructed_filter(x, attr_str=attr_str, op=op, rvalue_str=rvalue_str):
                    attribute = getattr(x, attr_str)
                    return op(attribute, type(attribute)(rvalue_str))

                and_methods.append(constructed_filter)
            except Exception as e:
                logging.warning("Failed to build filter expression: %s", e)
                return None

        or_methods.append(and_methods)

    return lambda x: any(all(filter_method(x) for filter_method in and_chain) for and_chain in or_methods)
