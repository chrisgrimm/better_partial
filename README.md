# Better partial function application in Python

Install with:

```
pip install better-partial
```

My library provides both a more ergonomic and expressive way of partially applying functions than `functools.partial`.  We begin by decorating a function with our `partial` operator. Let's consider the following function:

```python
from better_partial import partial, _
# Note that "_" can be imported under a different name if it clashes with your conventions

@partial
def f(a, b, c, d, e):
  return a, b, c, d, e
```

We can then evaluate `f` like a standard function:
```python
f(1, 2, 3, 4, 5) # --> (1, 2, 3, 4, 5)
```
but under the hood, my decorator now enables partial applications of `f`. Suppose we wanted to produce a function with all of `f`'s arguments fixed except for `c`. We can accomplish this via the placeholder `_` as follows:
```python
g = f(1, 2, _, 3, 4)
g(3) # --> (1, 2, 3, 4, 5)
```

Alternatively, we might want to produce a function in which *only* `c` is specified. We can accomplish this using `...`:
```python
g = f(..., c=3)
g(1, 2, 4, 5) # --> (1, 2, 3, 4, 5)
```

`...` must be specified as the last positional argument and indicates that all following positional arguments should be treated as placeholders. This means that we can specify `a` and `d` as follows:
```python
g = f(1, ..., d=4)
g(2, 3, 5) # --> (1, 2, 3, 4, 5)
```

The functions returned by partial applications are themselves partially applicable:
```python
g = f(..., e=5)
h = g(_, 2, 3, 4)
h(1) # --> (1, 2, 3, 4, 5)
```

This enables a diversity of ways to partially apply functions. Consider the following equivalent expressions for `(1, 2, 3, 4, 5)`:
```python
f(1, 2, 3, 4, 5)
f(_, 2, _, 4, _)(1, 3, 5)
f(..., e=5)(..., d=4)(1, 2, 3)
f(1, ..., e=5)(2, ..., d=4)(3)
f(_, _, _, _, _)(1, 2, 3, 4, 5)
```

