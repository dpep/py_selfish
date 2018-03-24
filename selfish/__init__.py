__author__ = 'dpepper'
__version__ = '0.1.0'


__all__ = [ 'selfish' ]


import types

from functools import wraps
from inspect import getmembers, isclass

from ambiguous import decorator



@decorator
def selfish(obj, name='self'):
  if type(obj) == types.FunctionType:
    method = obj

    if getattr(method, '_selfish', False):
      # already selfish
      return method

    if name in method.__code__.co_freevars:
      # variable is already bound by a closure and
      # can not be changed
      raise ValueError(
        "variable with same name already exists in closure: %s" % name
      )

    @wraps(method)
    def wrapper(*args, **kwargs):
      # preserve globals
      key_existed = method.__globals__.has_key(name)
      old_val = method.__globals__[name] if key_existed else None

      # update globals with magic self
      method.__globals__[name] = args[0]

      # make method call, omitting the implicit first arg
      res = method(*args[1:], **kwargs)

      # restore globals
      if key_existed:
        # unless the value has been changed by the method
        if method.__globals__[name] == args[0]:
          method.__globals__[name] = old_val
      else:
        del method.__globals__[name]

      return res

    # annotate method as selfish
    setattr(wrapper, '_selfish', name)
    return wrapper

  elif isclass(obj):
    # make all class instance methods selfish
    cls = obj

    for (method_name, method) in getmembers(cls):
      if type(method) != types.MethodType:
        # not a class method
        continue

      if cls != (method.im_self or method.im_class):
        # skip inherited methods
        continue

      wrapper = selfish(method.im_func, name)

      if method.im_self:
        # class method
        wrapper = classmethod(selfish(method.im_func, name))

      # bind new selfish method to class
      setattr(cls, method.__name__, wrapper)

    return obj

  else:
    raise ValueError("type not supported: %s" % obj)
