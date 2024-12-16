def collatz(n: int):
    while n != 1:
        print(n)
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3*n + 1
    print(n)

def main(n: int):
    collatz(n)

#!#

import sys
main(int(sys.argv[1]))
