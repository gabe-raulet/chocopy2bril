
def gcd1(a, b):
    if b == 0:
        return a
    else:
        return gcd1(b, a % b)

def gcd2(a, b):
    while b != 0:
        t = a
        a = b
        b = t % b
    return a

a = 25
b = 10
gcd_ab1 = gcd1(a, b)
gcd_ab2 = gcd2(a, b)
print(gcd_ab1)
print(gcd_ab2)
