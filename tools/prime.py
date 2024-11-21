
# Get the nth prime starting from 2

def get_prime(n: int) -> int:
    candidate: int = 2
    found: int = 0
    while True:
        if is_prime(candidate):
            found = found + 1
            if found == n:
                return candidate
        candidate = candidate + 1
    return 0 # should never happen

def is_prime(x: int) -> bool:
    div: int = 2
    while div < x:
        if x % div == 0:
            return False
        div += 1
    return True

# input parameter
n: int = 15

i: int = 1 # Run [1,n]

# do computations

while i <= n:
    print(get_prime(i))
    i+=1
