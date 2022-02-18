# Better Partial

I find `functools.partial` unintuitive so I coded up a better version.

```python
from better_partial import partial, _

@partial
def f(x, y, z, c=4):
  return x, y, z, c
  
f(1, 2, 3)  # (1, 2, 3, 4)
g = f(1, _, 3)  # returns a function
g(2)  # (1, 2, 3)

# You can partially evaluate partially evaluated functions
g = f(_, _, 3)
h = g(1, _)
h(2)  # (1, 2, 3)

# Works with keyword arguments as well
g = f(_, _, _, c=10)
g(1,2,3)  # (1, 2, 3, 10)

g = f(_, 0, _, c=10)
g(1,1)  # (1, 0, 1, 10)

g = f(1, 2, 3, c=_)
g(c=10)  # (1, 2, 3, 10)
```


I think `functools.partial` behaves unintuitively when you use it with functions with positional arguments. Here's an example:

```python
import functools

def f(x, y, z):
  return x, y, z
 
g = functools.partial(f, y=2)
g(1, 2)
```

Results in

```python
TypeError: f() got multiple values for argument 'y'
```
