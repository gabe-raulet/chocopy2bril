a = 1960
d = a - 235
b = 370
c = b

while b != 0:
    t = a
    a = b
    b = t % a

print(a)

if b == c:
    a = 0
else:
    b = c - (10 + 10)
    a = d + 235

tmp = a
a = b
b = tmp

while a != 0:
    t = b
    b = a
    a = t % b

print(b)
