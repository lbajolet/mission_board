# Mission Order

Understanding this piece of code is key to unlocking the way to the dome from the sewers. It is a two part mechanism. If you can find a way through the first part, we will send you the second part.

```
def bar(n, m):
    def foo(a): return 1
    for i in range(0, n+1):
        def foo(a, b=foo, j=i):
            if a <= 0 or a >= j:
                return 1
            else:
                return b(a-1) + b(a)
    return foo(m)
```

**Mission Type:** Reverse-Engineering... kind of...

**Objectives:** Find what this function does. it matches '^[a-z]+'s [a-z]+$'
