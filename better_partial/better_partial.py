class Unsupplied:
  pass

_ = Unsupplied()

def partial(fn):
  def g(*partial_args, **partial_kwargs):
    all_unsupplied = False
    if any(arg is Ellipsis for arg in partial_args):
      assert len(partial_args) == 1
      all_unsupplied = True
    
    unsupplied_arg_positions = [i for i, arg in enumerate(partial_args) if arg is _]
    unsupplied_kwargs = {key: value for key, value in partial_kwargs.items() if value is _}
    if len(unsupplied_arg_positions) == 0 and len(unsupplied_kwargs) == 0 and (not all_unsupplied):
      return fn(*partial_args, **partial_kwargs)
    @partial
    def h(*args, **kwargs):
      nonlocal partial_args, all_unsupplied
      partial_args = list(args) if all_unsupplied else list(partial_args)
      for i, arg in zip(unsupplied_arg_positions, args):
        partial_args[i] = arg
      for key, value in kwargs.items():
        partial_kwargs[key] = value
      partial_args = tuple(partial_args)
      return fn(*partial_args, **partial_kwargs)
    return h
  return g

if __name__ == '__main__':
  @partial
  def f(a, b, c):
    return (a, b, c)
  
  print('f(1,2,3)', f(1,2,3))
  g = f(1, _, 3)
  print('g(2)', g(2))
  g = f(1, _, _)
  h = g(_, 3)
  print('h(2)', h(2))
