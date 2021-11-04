class WithMetaMixin(object):

    _meta = None

    def __new__(cls, meta, value):
        # S = super()
        # obj = super().__new__(cls, meta, value)
        return super().__new__(cls, value)

    def __init__(self, meta, value):
        self._meta = meta
        try:
            type(value).__init__(self, value)
        except:
            pass

    def __getattr__(self, name):
        try:
            return super(WithMetaMixin, self).__getattr__(self, name)
        except:
            return self._meta.get(name)


    def __dir__(self):
        return list(self._meta.keys())
    def dir(self):
        return self.__dir__()
    @property
    def meta(self):
        return self._meta
    @property
    def obj(self):
        return self._obj


class DirAppendingWithMetaMixin(object):

    _meta = None


    def __new__(cls, meta, value):
        obj = super(DirAppendingWithMetaMixin, cls).__new__(cls, value)
        return obj

    def __init__(self, meta, value):
        self._meta = meta
        try:
            type(value).__init__(self, value)
        except:
            pass

    def __getattr__(self, name):
        try:
            return super(DirAppendingWithMetaMixin, self).__getattr__(self, name)
        except:
            return self._meta.get(name)

    def __dir__(self):
        return list(self._meta.keys()) + object.__dir__(self)

    @property
    def meta(self):
        return self._meta

class StringWithMeta(WithMetaMixin, str):
    pass


def patch_meta(meta, obj, append_dir=False):
    if obj is None:
        return obj
    if isinstance(obj, bool):
        obj = str(obj)
    mixin_class = DirAppendingWithMetaMixin if append_dir else WithMetaMixin
    new_type = type(type(obj).__name__ + '_with_meta', (mixin_class, type(obj)), {})
    return new_type(meta, obj)
