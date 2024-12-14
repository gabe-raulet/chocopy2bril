
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

def quadratic(a: int, b: int, c: int):

    Y: int = 0
    X: int = 0

    Y = sqrt(b*b - 4*a*c)
    X = -b

    print((X + Y) // (2 * a))
    print((X - Y) // (2 * a))

def main(a: int, b: int, c: int):
    quadratic(a, b, c)

#### TMP #####

#  quadratic(1, -4, -21) -> (7, -3)
#  quadratic(1 -4, 4) -> (2, 2)
#  quadratic(3, 3, -6)

import sys
main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
