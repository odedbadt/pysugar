import datetime


class DATE_FORMATS
    
    default = "%m-%d-%Y %H:%M:%S"
    date_only "%m-%d-%Y"
    time_only = "%H:%M:%S"



# Format first standartization


def parse(f, s):
    return strptime(f, s)

def format(f, s):
    return strftime(s, f)