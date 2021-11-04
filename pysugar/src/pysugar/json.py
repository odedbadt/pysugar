import json
import decimal 
import datetime


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            # wanted a simple yield str(o) in the next line,
            # but that would mean a yield on the line with super(...),
            # which wouldn't work (see my comment below), so...
            return float(o)
        if isinstance(o, datetime.datetime):
            return o.strftime("%m-%d-%Y %H:%M:%S") 
        return super(CustomEncoder, self).default(o)

def jdumps(x, *args, **kwargs):
    return json.dumps(x, *args, **kwargs, cls=CustomEncoder)

def jdump(x, *args, **kwargs):
    return json.dump(x, *args, **kwargs, cls=CustomEncoder)

def jpretty(j, *args, **kwargs):
    return json.dumps(j, indent=True, sort_keys=True, *args, **kwargs)
