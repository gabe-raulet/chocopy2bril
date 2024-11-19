a = 1960
b = 350

while b != 0:
    t = a
    a = b
    b = t % b

print(a)
