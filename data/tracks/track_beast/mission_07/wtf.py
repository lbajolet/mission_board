def bar(n, m):
    def foo(a): return 1
    for i in range(0, n+1):
        def foo(a, b=foo, j=i):
            if a <= 0 or a >= j:
                return 1
            else:
                return b(a-1) + b(a)
    return foo(m)
