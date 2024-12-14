def gcd(a: int, b: int) -> int:
    while a != b:
        if a > b:
            a = a - b
        else:
            b = b - a
    return a

def relative_primes(a: int):
    n: int = 1
    while n <= a:
        if gcd(n, a) == 1:
            print(n)
        n = n + 1

def main(a: int):
    relative_primes(a)

#### TMP #####

import sys
main(int(sys.argv[1]))
