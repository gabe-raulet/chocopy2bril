# prog5.py

# stmts: yes
# var_defs: yes
# func_defs: yes

var1: int = 150
var2: bool = True

def f1(a: int):
    print(a)

def f2(b: int) -> int:
    return b

var3: int = 11

def f3(a: int, b: int, c: bool) -> bool:
    var1: int = 15235
    var2: bool = True
    print(a)
    print(b)
    print(c)
    print(var1)
    print(var2)
    return var2


f1(var1)
var1 = f2(var1)
var1 = f2(23)

print(var1)
print(f1(var1))
print(f3(5, var1, var2))
