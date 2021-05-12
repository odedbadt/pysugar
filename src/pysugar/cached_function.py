cache = {}

#
# Creates a cache key from file name, function name and arguments
def _cache_key(file_name, function_name, args, kwargs):
    return (file_name,
            function_name,
            tuple([repr(x) for x in args]),
            tuple([(repr(x),repr(y)) for x in kwargs.items()])),

# Caches function resulst, use wisely:
# * Only use for functions that always return the same value for same inputs, DB dependant are a bad choice
# * do not use if arguments are convoluted as creating a cache key from them might be heavier than re running the function 

def cached_function(f):
    def g(*args, **kwargs):
        key = _cache_key(f.__code__.co_filename, f.__name__, args, kwargs)
        if key in cache:
            return cache[key]
        else:
            v = f(*args, **kwargs)
            cache[key] = v
            return v
    return g