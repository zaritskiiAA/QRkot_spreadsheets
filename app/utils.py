import copy
from collections.abc import Iterable


def get_spreadsheet_json(data: Iterable) -> Iterable:
    return copy.deepcopy(data)
