from collections import defaultdict, Iterable
from .functional import *
import re
from .metadata_mixin import patch_meta


DICT_KEY_RE = re.compile(r'$[A-Za-z][A-Za-z0-9_]*^')
DICT_KEY_ILLEGAL = re.compile(r'[^A-Za-z0-9_]')
DICT_KEY_ILLEGAL_PREFIX = re.compile(r'^([^A-Za-z_].*)')

def to_dict_key(non_key):
    non_key = str(non_key)
    if DICT_KEY_RE.match(non_key):
        return non_key
    return DICT_KEY_ILLEGAL.sub('_', DICT_KEY_ILLEGAL_PREFIX.sub(r'K_\1', non_key))

def drill(strct, path, str_path=''):
    if len(path) == 0:
        return strct
    path_element = path[0]
    if isinstance(strct, dict):
        _iterating_function = lambda s: s.items()
    elif isinstance(strct, Iterable):
        _iterating_function = enumerate
    else:
        # simple
        return drill(v, path[1:])
    _funtional = path_element if callable(path_element) else EQ(path_element)
    ret = {}
    for k, v in _iterating_function(strct):
        if _funtional(k):
            dict_key = to_dict_key(k)
            drilled_path = str_path + '.' + str(k)
            drilled_value = drill(v, path[1:], drilled_path)
            metadata = {'_path': drilled_path}
            if dict_key != k:
                metadata['_orig_key'] = k
            ret[dict_key] = patch_meta(metadata, drilled_value)
    return ret

def drillable_dict():
    return defaultdict(drillable_dict)

def drillable_to_standard_dict(drillable):
    if isinstance(drillable, dict):
        return {k: drillable_to_standard_dict(v) for k, v in drillable.items()}
    return drillable


class Envelope(object):
    wrapped = None

    def __init__(self, wrapped):
        self.wrapped = wrapped


class Deferred(object):
    def __init__(self, func):
        self.func = func
        self._value = None

    def __call__(self, *args, **kwargs):
        if self._value is None:
            self._value = self.func(*args, **kwargs)
        return self._value

class AttributeDict(object):
    def __init__(self, obj, depth=100, avoid={}):
        self._avoid = avoid
        self._depth = depth
        self._obj = obj
        if isinstance(obj, dict):
            self._index = {to_dict_key(k):v for
            k,v in obj.items()}
        elif isinstance(obj, list):
            self._index = {to_dict_key(j):v for
                j, v in enumerate(obj)}
        else:
            self._index = {}

    def __dir__(self):
        return self._index.keys()

    def __repr__(self):
        return self._obj.__repr__()

    def __getattr__(self, name):
        if name == '__orig':
            return self._obj
        if name in self._index.keys():
            value = self._index[name]
            if self._depth > 0:
                if isinstance(value, dict) or isinstance(value, Iterable):
                    return AttributeDict(value, self._depth - 1)
                if isinstance(value, Deferred):
                    return AttributeDict(value(), self._depth - 1)
                if isinstance(value, Envelope):
                    return value.wrapped
            return value
        else:
            return getattr(self._obj, name)
    def __getitem__(self, key):
        return self._obj[key]

    def __setitem__(self, key, value):
        self._obj[key] = value

    def __delitem__(self, key):
        self._obj.__delitem__(key)


