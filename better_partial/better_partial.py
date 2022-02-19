from inspect import signature, Parameter
from functools import wraps 
class Unsupplied:
  pass

_ = Unsupplied()

def _reinsert_kwargs(fn, args, kwargs):
  params = signature(fn).parameters
  param_position_mapping = {name: i for i, (name, param) in enumerate(params.items())
                            if param.default == Parameter.empty}
  
  # get all the kwargs that have positions make a new_kwargs dict that doesnt include them
  new_kwargs = {} 
  position_to_kwarg= {}
  for kw, arg in kwargs.items():
    if kw in param_position_mapping:
      position = param_position_mapping[kw]
      position_to_kwarg[position] = arg
    else:
      new_kwargs[kw] = arg
  
  # make a new list of arguments by inserting positional kwargs
  new_args = []
  arg_pos = 0
  for i in range(len(args) + len(position_to_kwarg)):
    if i in position_to_kwarg:
      new_args.append(position_to_kwarg[i])
    else:
      new_args.append(args[arg_pos])
      arg_pos += 1
  return new_args, new_kwargs

def _get_partial_signature(fn, partial_args, partial_kwargs):
  sig = signature(fn)
  params = list(sig.parameters.items())
  # remove args that are specified by partial_kwargs
  
  params = [(name, param) for name, param in params if partial_kwargs.get(name, _) is _]
  if partial_args[0] is Ellipsis:
    # if ... then we're done.
    pass
  else:
    assert len(partial_args) == len(params)
    params = [(name, param) for partial_arg, (name, param) in zip(partial_args, params)
              if partial_arg is _]
  return sig.replace(parameters=[param for name, param in params])
   
def partial(fn):
  @wraps(fn)
  def g(*partial_args, **partial_kwargs):
    all_unsupplied = False
    if any(arg is Ellipsis for arg in partial_args):
      assert len(partial_args) == 1
      all_unsupplied = True
    
    
    unsupplied_arg_positions = [i for i, arg in enumerate(partial_args) if arg is _]
    unsupplied_kwargs = {key: value for key, value in partial_kwargs.items() if value is _}
    if len(unsupplied_arg_positions) == 0 and len(unsupplied_kwargs) == 0 and (not all_unsupplied):
      return fn(*partial_args, **partial_kwargs)
    
    new_sig = _get_partial_signature(fn, partial_args, partial_kwargs)

    @partial
    def h(*args, **kwargs):
      nonlocal partial_args, partial_kwargs, all_unsupplied, unsupplied_arg_positions 
      _partial_args = list(partial_args).copy()
      _partial_kwargs = partial_kwargs.copy()
      _unsupplied_arg_positions = unsupplied_arg_positions.copy()
      _partial_args = list(args) if all_unsupplied else list(_partial_args)
      for i, arg in zip(_unsupplied_arg_positions, args):
        _partial_args[i] = arg
      for key, value in kwargs.items():
        _partial_kwargs[key] = value
      _partial_args, _partial_kwargs = _reinsert_kwargs(fn, _partial_args, _partial_kwargs)
      _partial_args = tuple(_partial_args)
      return fn(*_partial_args, **_partial_kwargs)
    h.__signature__ = new_sig 
    h.__wrapped__.__signature__ = new_sig 
    return h
    g.__signature__ = signature(f)
    g.__wrapped__.__signature__ = signature(f)
  return g


if __name__ == '__main__':
  @partial 
  def f(x, y, z):
    return x, y, z
  
  print(signature(f))
  g = f(..., y=2)
  print(signature(g))
  # print(g(1, 3))
  print(signature(g))

  h = g(..., z=3)
  print(signature(h))
  print(h(1))