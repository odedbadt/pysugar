from botocore.config import Config
import boto3
from .struct import AttributeDict, Deferred, to_dict_key
from functools import partial

client = boto3.client('ec2')


def instance_name(instance):
    if instance.tags:
        names = [t['Value'] for t in instance.tags if t['Key'] == 'Name']
        return names[0] if len(names) > 0 else instance.id
    else:
        return instance.id


def get_resources(region_name):
    resource =  boto3.resource('ec2', config=Config(region_name=region_name))
    instances = resource.instances.all()
    return {instance_name(instance): instance for instance in instances}


def init_ec2(regions=None):
    if regions is None:
        ec2 = boto3.client('ec2')
        regions = ec2.describe_regions()
    return AttributeDict({to_dict_key(region): Deferred(partial(get_resources, region)) for region in regions})
