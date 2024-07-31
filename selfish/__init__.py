__author__ = 'dpepper'
__version__ = '0.3.0'


__all__ = [ 'selfish' ]


from functools import wraps
from inspect import getmembers, isclass
from types import FunctionType, MethodType

from ambiguous import decorator


@decorator
def selfish(cls, name='self'):
    if not isclass(cls):
        raise ValueError('expected class, found: %s' % cls)

    # make all instance and class methods selfish
    for (method_name, method) in getmembers(cls):
        if type(method) not in [ FunctionType, MethodType ]:
            # not a class method
            continue

        if method_name not in cls.__dict__:
            # skip inherited methods
            continue

        # examine type of unbound method, since it's masked upon binding
        method_type = type(cls.__dict__[method_name])

        if method_type == staticmethod:
            # skip static methods since there is no self
            continue

        if name in method.__code__.co_freevars:
            # variable is already bound by a closure and
            # can not be changed
            raise NameError(
                "variable with same name already exists in closure: %s" % name
            )


        if method_type == classmethod:
            # create selfish wrapper around the underlying function, then
            # make it a classmethod
            wrapper = classmethod(create_wrapper(method.__func__, name))
        else:
            wrapper = create_wrapper(method, name)

        setattr(cls, method_name, wrapper)

    return cls


def create_wrapper(fn, name):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        # preserve globals
        key_existed = name in fn.__globals__
        old_val = fn.__globals__[name] if key_existed else None

        # update function namespace to include magic 'self'
        fn.__globals__[name] = self

        # make function call, omitting the implicit first arg
        res = fn(*args, **kwargs)

        # restore globals
        if key_existed:
            # unless the value has been changed by the function
            if fn.__globals__[name] == self:
                fn.__globals__[name] = old_val
        else:
            del fn.__globals__[name]

        return res

    return wrapper


# https://docs.python.org/3/howto/descriptor.html#functions-and-methods
