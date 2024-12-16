
def isqrt1(y: int) -> int:

    L: int = 0

    while (L+1) * (L+1) <= y:
        L = L + 1

    return L

def isqrt2(y: int) -> int:

    R: int = 0
    R = y

    while R * R > y:
        R = R - 1

    return R

def isqrt3(y: int) -> int:

    L: int = 0
    a: int = 1
    d: int = 3

    while a <= y:
        a = a + d
        d = d + 2
        L = L + 1

    return L

def isqrt4(y: int) -> int:

    L: int = 0
    M: int = 0
    R: int = 0

    R = y + 1

    while L != R - 1:

        M = (L + R) // 2

        if M * M <= y:
            L = M
        else:
            R = M

    return L

def isqrt5(s: int) -> int:

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

def isqrt6(n: int) -> int:

    small_cand: int = 0
    large_cand: int = 0

    if n < 2:
        return n

    small_cand = isqrt6(n // 4) * 2
    large_cand = small_cand + 1

    if large_cand * large_cand > n:
        return small_cand
    else:
        return large_cand

def main(y: int, v: int):
    if v == 1:
        print(isqrt1(y))
    elif v == 2:
        print(isqrt2(y))
    elif v == 3:
        print(isqrt3(y))
    elif v == 4:
        print(isqrt4(y))
    elif v == 5:
        print(isqrt5(y))
    elif v == 6:
        print(isqrt6(y))

#!#

import sys
main(int(sys.argv[1]), int(sys.argv[2]))
