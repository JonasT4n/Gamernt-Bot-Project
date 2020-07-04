class A:

    t: int = 7
    s: int = 9

    @property
    def data(self):
        return self.t, self.s

a = [A(), A()]
b = a[1]

del a[1]
del b

print(a)
print(b.t)