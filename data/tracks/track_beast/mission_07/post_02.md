# Mission Order

Good job on the first part. Here is the second part of the algorithm.

```
def bar(n, m):
    def foo(a, b): return a+1
    for i in range(0, n):
        def foo(a, b, c=foo):
            if a == 0:
                return c(1, c)
            else:
                return c(b(a-1, b), c)
    return foo(m, foo)
```

**Mission Type:** Reverse-Engineering... kind of...

**Objectives:** Find what this function returns for bar(3, 43)
