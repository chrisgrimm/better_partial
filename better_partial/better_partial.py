import inspect
from functools import wraps 
from inspect import Parameter
from typing import NamedTuple, Union, Tuple, Dict, Any, List
from enum import Enum


class FillingMode(Enum):
  NOT_FILLED = 0
  PLACEHOLDER = 1 
  FILLED_BY_DEFAULT = 2
  FILLED = 3


class Placeholder:
  pass 


_ = Placeholder()


Binding = Dict[str, Union[int, str, Tuple[int, str]]]
Filling = Dict[str, Tuple[FillingMode, Any]]


def create_binding(sig: inspect.Signature) -> Binding:
  param_to_accessor = {}
  for pos, (name, param) in enumerate(sig.parameters.items()):
    if param.kind == Parameter.POSITIONAL_ONLY:
      param_to_accessor[name] = pos
    elif param.kind == Parameter.KEYWORD_ONLY:
      param_to_accessor[name] = name
    else:
      param_to_accessor[name] = (pos, name)
  return param_to_accessor


def create_filling(sig: inspect.Signature, binding: Binding) -> Filling:
  filling = {}
  for name in binding:
    if sig.parameters[name].default != inspect._empty:
      filling[name] = (FillingMode.FILLED_BY_DEFAULT, sig.parameters[name].default)
    else:
      filling[name] = (FillingMode.NOT_FILLED, None)
  return filling


def update_filling(old_filling: Filling, binding: Binding, args: List[Any], kwargs: Dict[str, Any]) -> Filling:
  filling = old_filling.copy()

  position_to_params = {}
  for param, accessor in binding.items():
    if isinstance(accessor, int):
      position_to_params[accessor] = param
    elif isinstance(accessor, tuple):
      position_to_params[accessor[0]] = param
  
  for name, arg in kwargs.items():
    accessor = binding[name]
    if isinstance(accessor, int):
      raise Exception(f'Cannot fill position only argument "{name}" with keyword.')
    if filling[name][0] == FillingMode.FILLED:
      raise Exception(f'Argument "{name}" already filled.')
    if arg is _:
      filling[name] = (FillingMode.PLACEHOLDER, None)
    else:
      filling[name] = (FillingMode.FILLED, arg)
    
  for pos, arg in enumerate(args):
    if pos not in position_to_params:
      raise Exception(f'Function does not have argument with position {pos}.')
    name = position_to_params[pos]
    accessor = binding[name]
    if isinstance(accessor, str):
      raise Exception(f'Cannot fill keyword only argument "{name}" with positional argument.')
    if filling[name][0] == FillingMode.FILLED:
      raise Exception(f'Argument "{name}" already filled.')
    if arg is _:
      filling[name] = (FillingMode.PLACEHOLDER, None)
    else:
      filling[name] = (FillingMode.FILLED, arg)
  return filling


def raise_if_missing_argument(filling: Filling) -> bool:
  missing_args = []
  for name, (filling_mode, val) in filling.items():
    if filling_mode == FillingMode.NOT_FILLED:
      missing_args.append(name)
  if missing_args:  
    missing_args_string = ', '.join(f"{arg}" for arg in missing_args)
    raise Exception(f'Missing arguments: {missing_args_string}.')


def mark_not_filled_as_placeholders(old_filling: Filling) -> Filling:
  filling = {}
  for name, (filling_mode, val) in old_filling.items():
    if filling_mode == FillingMode.NOT_FILLED:
      filling[name] = (FillingMode.PLACEHOLDER, None)
    else:
      filling[name] = (filling_mode, val)
  return filling


def is_filling_complete(filling: Filling) -> bool:
  for name, (filling_mode, val) in filling.items():
    if filling_mode == FillingMode.PLACEHOLDER: 
      return False
  return True


def filling_to_args_kwargs(filling: Filling, binding: Binding) -> Tuple[List[Any], Dict[str, Any]]:
  positions_and_args = []
  kwargs = {}
  missing_args = []
  for name, (filling_mode, val) in filling.items():
    if filling_mode == FillingMode.PLACEHOLDER:
      missing_args.append(name)      
    if isinstance(binding[name], str):
      kwargs[name] = val
    elif isinstance(binding[name], tuple):
      positions_and_args.append((binding[name][0], val))
    else:
      positions_and_args.append((binding[name], val))
  args = [arg for pos, arg in sorted(positions_and_args, key=lambda x: x[0])]
  if missing_args:
    missing_args_string = ', '.join(f"{arg}" for arg in missing_args)
    raise Exception(f'Cannot construct args / kwargs. Missing arguments: {missing_args_string}.')

  return args, kwargs


def create_partial_signature(signature: inspect.Signature, binding: Binding, filling: Filling) -> inspect.Signature:  
  positional_only_with_positions = []
  for name, accessor in binding.items():
    if isinstance(accessor, int):
      positional_only_with_positions.append((accessor, name))
  positional_only = [name for pos, name in sorted(positional_only_with_positions, key=lambda x: x[0])]

  positional_or_kw_with_positions = []
  for name, accessor in binding.items():
    if isinstance(accessor, tuple):
      positional_or_kw_with_positions.append((accessor[0], name))
  positional_or_kw = [name for pos, name in sorted(positional_or_kw_with_positions, key=lambda x: x[0])]

  kw_only = []
  for name, accessor in binding.items():
    if isinstance(accessor, str):
      kw_only.append(name)
  
  def _make_parameter_and_append(name, kind):
    if filling[name][0] == FillingMode.PLACEHOLDER:
      parameters.append(Parameter(name, kind))
    elif filling[name][0] == FillingMode.FILLED_BY_DEFAULT:
      parameters.append(Parameter(name, kind, default=signature.parameters[name].default))

  parameters = []
  for name in positional_only:
    _make_parameter_and_append(name, Parameter.POSITIONAL_ONLY)
  for name in positional_or_kw:
    _make_parameter_and_append(name, Parameter.POSITIONAL_OR_KEYWORD)
  for name in kw_only:
    _make_parameter_and_append(name, Parameter.KEYWORD_ONLY)
  return inspect.Signature(parameters)


def partial(f):
  outer_sig = inspect.signature(f)

  for param in outer_sig.parameters.values():
    if param.kind == Parameter.VAR_KEYWORD or param.kind == Parameter.VAR_POSITIONAL:
      raise Exception('Better-Partial doesnt handle functions with variable positional or keyword arguments yet.')
    
  @wraps(f)
  def g(*partial_args, **partial_kwargs):
    outer_binding = create_binding(outer_sig)
    outer_filling = create_filling(outer_sig, outer_binding)
    
    ellipsis_count = sum(arg == Ellipsis for arg in partial_args)
    if ellipsis_count > 1:
      raise Exception('Only one Ellipsis can be in args.')
    if ellipsis_count == 1:
      if partial_args[-1] != Ellipsis:
        raise Exception('Ellipsis must be the last positional argument.')

      outer_filling = mark_not_filled_as_placeholders(outer_filling)
      partial_args = partial_args[:-1]
  
    outer_filling = update_filling(outer_filling, outer_binding, partial_args, partial_kwargs)
    raise_if_missing_argument(outer_filling)

    if is_filling_complete(outer_filling):
      filled_args, filled_kwargs = filling_to_args_kwargs(outer_filling, outer_binding)
      return f(*filled_args, **filled_kwargs)    

    inner_sig = create_partial_signature(outer_sig, outer_binding, outer_filling)
    inner_binding = create_binding(inner_sig)
    def h(*args, **kwargs):
      # use the inner binding to update the filling
      updated_filling = update_filling(outer_filling, inner_binding, args, kwargs)
      # use the outer binding to get the args / kwargs from the filling
      filled_args, filled_kwargs = filling_to_args_kwargs(updated_filling, outer_binding)
      return f(*filled_args, **filled_kwargs)
    h.__signature__ = inner_sig
    return partial(h) 
    g.__signature__ = outer_sig
  return g
