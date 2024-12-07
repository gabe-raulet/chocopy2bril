
def func_or(a: bool, b: bool) -> bool:
    return a or b

def func_and(a: bool, b: bool) -> bool:
    return a and b

def func_xor(a: bool, b: bool) -> bool:
    return (a and not b) or ((not a) and b)

print(0)

print(func_or(True, True))
print(func_or(True, False))
print(func_or(False, True))
print(func_or(False, False))

print(1)

print(func_and(True, True))
print(func_and(True, False))
print(func_and(False, True))
print(func_and(False, False))

print(2)

print(func_xor(True, True))
print(func_xor(True, False))
print(func_xor(False, True))
print(func_xor(False, False))
