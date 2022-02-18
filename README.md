# Better partial function application in Python

I find `functools.partial` unintuitive so I coded up a better version.

```python
from better_partial import partial, _, ___

@partial
def f(x, y, z, c=4):
  return x, y, z, c

# If you use the function normally, nothing unusual happens
f(1, 2, 3)  # (1, 2, 3, 4)
# But now you can pass placeholders in to do partial function application!
g = f(1, _, 3)  # returns a function
g(2)  # (1, 2, 3)

# You can partially evaluate partially evaluated functions
g = f(_, _, 3)
h = g(1, _)
h(2)  # (1, 2, 3)

# Works with keyword arguments as well
g = f(_, _, _, c=10)
g(1,2,3)  # (1, 2, 3, 10)

# Alternatively you can write
g = f(___, c=10)
g(1,2,3)  # (1, 2, 3, 10)

# Can mix and match
g = f(_, 0, _, c=10)
g(1,1)  # (1, 0, 1, 10)

g = f(1, 2, 3, c=_)
g(c=10)  # (1, 2, 3, 10)
```
