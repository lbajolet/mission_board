def bar(n, m):
    def foo(a, b): return a+1
    for i in range(0, n):
        def foo(a, b, c=foo):
            if a == 0:
                return c(1, c)
            else:
                return c(b(a-1, b), c)
    return foo(m, foo)
