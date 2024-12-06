import sys
import json
import pprint

def del_nulls(d):
    return {key : val for key, val in d.items() if bool(val)}

def read_var_defs(var_defs):
    types, inits = {}, {}
    for var_def in var_defs:
        name = var_def["typed_var"]["id"]
        types[name] = var_def["typed_var"]["type"]
        inits[name] = var_def["literal"]
    return types, inits

def read_func_def(func_def):
    var_defs = func_def["func_body"]["var_defs"]
    types, inits = read_var_defs(var_defs)


def read_func_defs(func_defs):
    funcs = {}
    for func_def in func_defs:
        name = func_def.pop("name")
        funcs[name] = read_func_def(func_def)
    return funcs

#  if __name__ == "__main__":
    #  program = json.load(sys.stdin)

program = json.load(open("prog.json"))

decls = program["decls"]
stmts = program["stmts"]

var_defs = decls["var_defs"]
func_defs = decls["func_defs"]

types, inits = read_var_defs(var_defs)

