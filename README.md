# Better partial function application in Python

Install with:

```
pip install better-partial
```

I find `functools.partial` unintuitive so I coded up a better version. Let's play around with it. You apply it as a decorator to your functions:

```python
import better_partial as bp

@bp.partial
def some_operation(x, p1, p2):
  return (x + p1) * p2
```

On the surface nothing really changes. `some_operation` behaves just like a normal function when you pass it values

```python
some_operation(1, 2, 3)  # --> 9
```

but under the hood my `partial` decorator is working all kinds of magic. Imagine you need to pass a function of `x` to some other part of your codebase and `some_operation`, with a particular setting of `p1 = 10` and `p2 = 20`, fits the bill. In order to make this work, you'd have to wrap `some_operation` like this:

```python
func = lambda x: some_operation(x, 10, 20)
```

or this

```python
def func(x):
  return some_operation(x, 10, 20)
```

The `bp.partial` decorator makes this a bit nicer. By supplying a `bp._` placeholder for any argument in `some_operation` we can produce a new function where the variables replaced by `bp._` are omitted:
```python
func = some_operation(bp._, 10, 20)
func(x) == some_operation(x, 10, 20)  # --> True
```

You can replace any positional arguments with `bp._` to perform partial function applications
```python
@bp.partial
def f(a, b, c, d, e):
  return a + b + c + d + e
  
g = f(bp._, 0, bp._, 0, bp._)
g(1, 3, 5)  # --> 1 + 0 + 3 + 0 + 5
```

The functions produced by these partial applications also support further partial application. Consider using the `g` from above again:
```python
h = g(1, bp._, bp._)
h(3, 5)  # --> 1 + 0 + 3 + 0 + 5
```

This is great if you want to omit a few parameters and specify the rest, but what if it's the other way around? You just want to fix the values of a few parameters. `better_partial` lets you do this. Consider `f` from above and suppose that we want to fix `c = 5` and `a = 7`, you can do this too:
```python
g = f(..., c=5, a=7)

g(0, 0, 0)  # --> 7 + 0 + 5 + 0 + 0
g(0, 0, 0) == f(7, 0, 5, 0, 0) == f(7, bp._, 5, bp._, bp._)(0, 0, 0)  # --> True
```

`better_partial` lets you use the `...` sentinel to indicate that you _only_ want to specify the values of what follows.

An easy way to appreciate the flexibility and power of the `partial` operator is to see the variety of ways you can evaluate functions with it. Using the definition of `f` from above, all of the following lines are equivalent:

```python
f(1,2,3,4,5)
f(bp._, 2, bp._, 4, bp._)(1, 3, 5)
f(..., b=2, d=4)(1, 3, 5)
f(..., b=2, d=4)(1, bp._, 5)(3)
f(..., b=2, d=4)(..., c=3)(1, 5)
```
