
def func1() -> int:
    return 15

def func2() -> bool:
    return True

def func3(a: int, b: int, c: bool, d: bool) -> int:
    return b

print(func1())
print(func2())
print(func3(1, 2, 3, True))
