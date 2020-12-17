from collections import defaultdict
from .functional import *
import re
from .metadata_mixin import patch_meta
def drillable_dict():
    return defaultdict(drillable_dict)

def drillable_to_standard_dict(drillable):
    if isinstance(drillable, dict):
        return {k: drillable_to_standard_dict(v) for k, v in drillable.items()}
    return drillable

DICT_KEY_RE = re.compile(r'[A-Za-z][A-Za-z0-9_]+')
DICT_KEY_ILLEGAL = re.compile(r'[^A-Za-z0-9_]')
def to_dict_key(non_key):
    if DICT_KEY_RE.match(non_key):
        return non_key
    return '_' + DICT_KEY_ILLEGAL.subs('_', non_key)

def drill(strct, path_element):
    if isinstance(strct, dict):
        _iterating_function = lambda s: s.items()
    elif isinstance(strct, Iterable):
        _iterating_function = enumerate
    else:
        # simple
        return strct
    _funtional = path_element if callable(path_element) else EQ(path_element)
    ret = {}
    for k, v in _iterating_function(strct):
        if _funtional(k):
            ret[to_dict_key(k)] = patch_meta({'_orig_key': k}, v)
    return ret
