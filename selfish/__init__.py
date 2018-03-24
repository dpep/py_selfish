__author__ = 'dpepper'
__version__ = '0.2.0'


__all__ = [ 'selfish' ]


from types import MethodType

from functools import wraps
from inspect import getmembers, isclass

from ambiguous import decorator



@decorator
def selfish(cls, name='self'):
  if not isclass(cls):
    raise ValueError("expected class, found: %s" % cls)

  # make all instance and class methods selfish
  for (method_name, method) in getmembers(cls):
    if type(method) != MethodType:
      # not a class method
      continue

    if cls != (method.im_self or method.im_class):
      # skip inherited methods
      continue

    # instance method
    wrapper = _selfish_wrapper(method.im_func, name)

    if method.im_self:
      # class method
      wrapper = classmethod(wrapper)

    # bind new selfish method to class
    setattr(cls, method.__name__, wrapper)

  return cls


def _selfish_wrapper(function, name):
  if name in function.__code__.co_freevars:
    # variable is already bound by a closure and
    # can not be changed
    raise ValueError(
      "variable with same name already exists in closure: %s" % name
    )

  @wraps(function)
  def wrapper(*args, **kwargs):
    # preserve globals
    key_existed = function.__globals__.has_key(name)
    old_val = function.__globals__[name] if key_existed else None

    # update globals with magic self
    function.__globals__[name] = args[0]

    # make function call, omitting the implicit first arg
    res = function(*args[1:], **kwargs)

    # restore globals
    if key_existed:
      # unless the value has been changed by the function
      if function.__globals__[name] == args[0]:
        function.__globals__[name] = old_val
    else:
      del function.__globals__[name]

    return res

  return wrapper
