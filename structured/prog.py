var1: int = None
var2: int = 15
var3: bool = False

def func1(a: int, b: bool) -> int:
    var1: bool = False
    return a

var2 = func1(15, var3)
print(var2)
