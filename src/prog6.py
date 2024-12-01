var1: int = 15
var2: int = 10

def are_equal(a: int, b: int) -> bool:
    result: bool = False
    result = (a == b)
    return result

var3: int = 135135

print(are_equal(var1, var2))
print(are_equal(var1, var2 + 5))
