var1: int = None
var2: int = 15
var3: bool = False

def func1(a: int, b: bool) -> int:
    var1: bool = False
    print(var1)
    return var1

def f():
    pass

v: int = 9154235
v = func1(var2, False)
v = func1(var2, var3)

print(v)
print(var2)
print(4)
print(False)

f()

print(func1(1, True))

#  var2 = func1(15, var3)
#  print(var2)

#  func2(14)
#  func2(var2)

#  print(v)
#  func2(v)
