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

from pysugar import aws
from pysugar.struct import AttributeDict, to_dict_key, DICT_KEY_ILLEGAL, DICT_KEY_RE

regions = aws.init_ec2(['eu-west-1', 'eu-central-1'])

regions.eu_west_1.event_store_01.public_dns_name

AttributeDict({'eu-x':9})

# +
import re
DICT_KEY_RE = re.compile(r'$[A-Za-z][A-Za-z0-9_]*^')
DICT_KEY_ILLEGAL = re.compile(r'[^A-Za-z0-9_]')
DICT_KEY_ILLEGAL_PREFIX = re.compile(r'^([^A-Za-z_].*)')

def to_dict_key(non_key):
    non_key = str(non_key)
    if DICT_KEY_RE.match(non_key):
        return non_key
    return DICT_KEY_ILLEGAL.sub('_', DICT_KEY_ILLEGAL_PREFIX.sub(r'K_\1', non_key))


# -

to_dict_key('8-9')

import boto3
ec2 = boto3.client('ec2')
regions = ec2.describe_regions()
print(regions)


