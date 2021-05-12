from collections import defaultdict, Iterable
from collections.abc import Collection
from .functional import *
from .cached_function import cached_function
import re
from .metadata_mixin import patch_meta, WithMetaMixin
import json
from .functional import *
DICT_KEY_RE = re.compile(r'$[A-Za-z][A-Za-z0-9_]*^')
DICT_KEY_ILLEGAL = re.compile(r'[^A-Za-z0-9_]')
DICT_KEY_ILLEGAL_PREFIX = re.compile(r'^([^A-Za-z_].*)')


@cached_function
def to_dict_key(non_key):
    if isinstance(non_key, int):
        return f'K_{non_key}'
    if non_key.startswith('_'):
        non_key = 'u' + non_key
    non_key = str(non_key)
    if DICT_KEY_RE.match(non_key):
        return non_key
    v = DICT_KEY_ILLEGAL.sub('_', DICT_KEY_ILLEGAL_PREFIX.sub(r'K_\1', non_key))
    return v

def merge(*args):
    ret = {}
    for d in args[::-1]:
        if d is None:
            continue
        for k,v in d.items():
            ret[k]=v
    return {k:v for k, v in ret.items() if v is not None}

def drill(strct, path, str_path=''):
    if isinstance(strct,str):
        try:
            strct = json.loads(strct)
        except:
            pass
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


## AttributeDict

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

class Mask(object):
    def __init__(self, obj, mask):
        self._mask = mask
        self._obj = obj

class AttributeDict(object):
    def __init__(self, obj, depth=100, avoid={}):
        if isinstance(obj, str):
            try:
                obj = json.loads(obj)
            except:
                pass
        self._avoid = avoid
        self._depth = depth
        self._obj = obj
        if isinstance(obj, Mask):
            self._index = {to_dict_key(k): v for
            k, v in obj.meta.items()}
        elif isinstance(obj, dict):
            self._index = type(obj)([(to_dict_key(k), v) for
            k, v in obj.items()])
        elif isinstance(obj, list):
            self._index = {to_dict_key(j): v for
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
                if isinstance(value, dict) or isinstance(value, list):
                    return AttributeDict(value, self._depth - 1)
                if isinstance(value, WithMetaMixin):
                    return AttributeDict(value.meta, self._depth - 1)
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


def _find_in_struct_rec(s, expression, path=[]):
    if isinstance(s,str):
        try:
            s = json.loads(s)
        except:
            pass
    if isinstance(s, dict):
        res = []
        for k, v in s.items():
            local_path = path + [k]
            if expression in k:                
                res.append((local_path, v))
            res = res + _find_in_struct_rec(v, expression, local_path)
        return res
    if isinstance(s, list):
        res = []
        for j, v in enumerate(s):
            local_path = path + [j]            
            res = res + _find_in_struct_rec(v, expression, local_path)
        return res
    if str(expression) in str(s):
        return [(path, s)]
    return []


def find_in_struct(s, expression):
    if isinstance(s,str):
        try:
            s = json.loads(s)
        except:
            pass
    paths = _find_in_struct_rec(s, expression)
    index = {}
    for path, v in paths:
        pretty = '.'.join([str(frag) for frag in path])

        index[pretty] = Envelope(patch_meta({
            'pretty': pretty,
            'path': path
            },v))
    return AttributeDict(index)


def lgroupby(l, g):
    f2 = identity
    if isinstance(g, str):
        l1 = l 
        f1 = lambda x: x[g]
    elif callable(g):
        l1 = l
        f1 = g
    elif isinstance(g, list):
        l1 = zip(l, g)
        f1 = lambda x: x[1]
        f2 = lambda x: x[0]
    res = []
    k = None
    for x in l1:        
        if k != f1(x):
            print(x, k, f1(x), f2(x))
            k = f1(x)
            res.append([])
        res[-1].append(f2(x))
    return res
