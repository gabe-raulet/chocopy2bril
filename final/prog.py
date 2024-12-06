var_int_1: int = 1
var_int_123: int = 123
var_int_null: int = None

var_bool_false: bool = False
var_bool_true: bool = True
var_bool_null: bool = None

print(var_int_1)
print(1)

print(var_int_123)
print(123)

print(var_int_null)
print(0)

print(var_bool_false)
print(False)

print(var_bool_true)
print(True)

print(var_bool_null)
print(False)


print(var_int_1)
var_int_1 = 2
print(var_int_1)
var_int_1 = var_int_123
print(var_int_1)
var_int_1 = None
print(var_int_1)

print(var_bool_false)

var_bool_false = True
print(var_bool_false)

var_bool_false = None
print(var_bool_false)

var_bool_false = var_bool_true
print(var_bool_false)

var_bool_false = var_bool_null
print(var_bool_false)

