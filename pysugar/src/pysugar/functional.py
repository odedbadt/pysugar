def identity(x):
    return x

def Always(*args, **kwargs):
    return True

def Never(*args, **kwargs):
    return Fasle

def Constant(x, *args, **kwargs):
    return x

def OR(f, g):
    def _or(*args, **kwargs):
        return f(*args, **kwargs) or g(*args, **kwargs)
    return _or

def AND(f, g):
    def _and(*args, **kwargs):
        return f(*args, **kwargs) and g(*args, **kwargs)
    return _and

def NOT(f, g):
    def _not(*args, **kwargs):
        return not f(*args, **kwargs)
    return _not

def IN(s):
    def _in(x):
        return x in s
    return _in

def NOT_IN(s):
    def _in(x):
        return x not in s
    return _in

def IN(s):
    def _in(x):
        return x in s
    return _in

def NOT_IN(s):
    def _in(x):
        return x not in s
    return _in

def EQ(x):
    def _eq(y, *args, **kwargs):
        return x == y
    return _eq


class O:
    def __init__(self, obj):
        self._obj = obj

    def __getattr__(self, attr):
        try:
            return self._obj.__getattribute__(attr)
        except AttributeError:
            return None
    def __call__(self, *args, **kwargs):
        try:
            return self._obj.__call__(*args, **kwargs)
        except AttributeError:
            return None
    def __getitem__(self, key):
        try:
            return self._obj.__getitem__(key)
        except AttributeError:
            return None

class G:
    def __init__(self, prop):
        self._prop = prop

    def __call__(self, *args, **kwargs):
        try:
            return args[0][prop]
        except AttributeError:
            return None

