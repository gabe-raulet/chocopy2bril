
# C(0) = 1
# C(n+1) = C(0)*C(n) + C(1)*C(n-1) + ... + C(n)*C(0)

# C(n) = C(0)*C(n-1) + C(1)*C(n-2) + ... + C(n-1)*C(0)
#      = sum_{0 <= i <= n-1}{C(i)*C(n-i-1)}

def catalan(n: int) -> int:
    i: int = 0
    c: int = 1
    if n == 0 or n == 1:
        return c
    c = 0
    while i < n:
        c += catalan(i) * catalan(n - i - 1)
        i = i + 1
    return c

def main(n: int):
    print(catalan(n))

#### TMP #####

import sys
main(int(sys.argv[1]))
