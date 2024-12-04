a: int = 0

def example_function_one(input1: int, input2: int, input3: bool) -> int:
    a: int = 0
    b: int = 0
    c: bool = False

    b = input1
    a = input2
    c = input3

    print(c)
    print(a)
    print(b)

    return b

a = example_function_one(188, a, True)

print(a)
print(example_function_one(a, 0, False))
