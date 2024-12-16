def sqrt(s: int) -> int:

    x0: int = 0
    x1: int = 0

    if s <= 1:
        return s

    x0 = s // 2
    x1 = (x0 + s // x0) // 2

    while x1 < x0:
        x0 = x1
        x1 = (x0 + s // x0) // 2

    return x0

def is_square(n: int) -> bool:
    i: int = 1
    while i*i < n:
        i = i + 1
    return (i*i == n)

def fermat_factor(n: int): # n should be odd

    a: int = 0
    b2: int = 0

    a = sqrt(n) + 1
    b2 = a*a - n

    while not is_square(b2):
        a = a + 1
        b2 = a*a - n

    print(a - sqrt(b2))
    print(a + sqrt(b2))

def main(n: int):
    fermat_factor(n)

#!#

import sys
main(int(sys.argv[1]))
