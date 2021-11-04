# ---
# jupyter:
#   jupytext:
#     formats: py,ipynb
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.7.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %load_ext autoreload
# %autoreload 2

from pysugar.struct import AttributeDict, Envelope, Deferred
from pysugar.functional import *

ad = AttributeDict({'x':Envelope({'y':[0]})})

ad.x['y']

type(tpl)

c2 = tpl[2]

issubclass(c2, c1)

import re
DICT_KEY_RE = re.compile(r'[A-Za-z][A-Za-z0-9_]+')
DICT_KEY_ILLEGAL = re.compile(r'[^A-Za-z0-9_]')

DICT_KEY_ILLEGAL.sub('_',  'a')


class C:
    class E:
        pass


C.E()


