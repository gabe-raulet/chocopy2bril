# gcd(u,0) = u
# gcd(2u,2v) = 2*gcd(u,v)
# gcd(u,2v) = gcd(u,v) if u is odd
# gcd(u,v) = gcd(u, v - u) if u,v odd and u <= v.

def gcd1(u: int, v: int) -> int:

    t: int = 0

    if u == 0:
        return v
    elif v == 0:
        return u
    elif u % 2 == 0 and v % 2 == 0:
        return 2 * gcd1(u // 2, v // 2)
    elif v % 2 == 0:
        return gcd1(u, v // 2)
    else:

        if u > v:
            t = u
            u = v
            v = t

        return gcd1(u, v - u)

def gcd2(u: int, v: int) -> int:

    t: int = 0
    k: int = 1

    if u == 0:
        return v

    if v == 0:
        return u

    while u % 2 == 0 and v % 2 == 0:
        k = k * 2
        u = u // 2
        v = v // 2

    while u > 0 and u % 2 == 0:
        u = u // 2

    while v > 0 and v % 2 == 0:
        v = v // 2

    while True:

        if u > v:
            t = u
            u = v
            v = t

        v = v - u

        if v == 0:
            return u * k

        while v > 0 and v % 2 == 0:
            v = v // 2

def gcd3(u: int, v: int) -> int:
    while u != v:
        if u > v:
            u = u - v
        else:
            v = v - u
    return u

def gcd4(u: int, v: int) -> int:
    if v == 0:
        return u
    else:
        return gcd4(v, u % v)


def gcd5(u: int, v: int) -> int:
    t: int = 0
    while v != 0:
        t = u
        u = v
        v = t % v
    return u

def main(a: int, b: int, v: int):
    if v == 1:
        print(gcd1(a, b))
    elif v == 2:
        print(gcd2(a, b))
    elif v == 3:
        print(gcd3(a, b))
    elif v == 4:
        print(gcd4(a, b))
    elif v == 5:
        print(gcd5(a, b))

#### TMP #####

import sys
main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
