var1: int = 15
var2: bool = False

def func1(a: int, b: int, c: bool) -> int:
    v1: int = 1515
    v2: bool = True
    print(v1)
    v1 = a
    v2 = c
    return b

print(var1)
var1 = func1(var1, 14, var2)
print(var1)
