a: int = 1960 # a
b: int = 350 # b

t: int = 0 # temporary

# while loop for euclidean division

while b != 0:
    t = a
    a = b #
    b = t % b

print(a)
