# Better partial function application in Python

Install with:

```
pip install better-partial
```

I find `functools.partial` unintuitive so I coded up a better version.

```python
import better_partial as bp

@bp.partial
def f(x, y, z, c=4):
  return x, y, z, c

# If you use the function normally, nothing unusual happens
f(1, 2, 3)  # (1, 2, 3, 4)
# But now you can pass placeholders in to do partial function application!
g = f(1, bp._, 3)  # returns a function
g(2)  # (1, 2, 3)

# You can partially evaluate partially evaluated functions
g = f(bp._, bp._, 3)
h = g(1, bp._)
h(2)  # (1, 2, 3)

# Works with keyword arguments as well
g = f(bp._, bp._, bp._, c=10)
g(1,2,3)  # (1, 2, 3, 10)

# Alternatively to omit all positional arguments, you can use
g = f(..., c=10)
g(1,2,3)  # (1, 2, 3, 10)

# You can also specify positional arguments using keyword arguments
g = f(..., y=2)
g(1, 3)  # (1, 2, 3, 4)


# Can mix and match
g = f(bp._, 0, bp._, c=10)
g(1,1)  # (1, 0, 1, 10)

g = f(1, 2, 3, c=bp._)
g(c=10)  # (1, 2, 3, 10)
```
