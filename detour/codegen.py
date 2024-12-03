import sys
import json
from lexer import *
from parser import *

#  text = open(fname).read()
tokens = list(lex_text(sys.stdin.read()))
parser = Parser(tokens)
prog = parser.parse()

def gen_var_defs(var_types, var_inits):
    instrs = []
    if not var_types or not var_inits: return instrs
    for name in var_inits:
        type = var_types[name]
        init = var_inits[name]
        instrs.append({"op" : "const", "dest" : name, "type" : type, "value" : init})
    return instrs

def gen_func_defs(func_defs):
    funcs = []
    if not func_defs: return funcs
    for func_def in func_defs:
        func = {}
        func["name"] = func_def["name"]
        func["instrs"] = gen_var_defs(func_def.get("var_types"), func_def.get("var_inits"))
        if "rtype" in func_def: func["type"] = func_def["rtype"]
        if "args" in func_def:
            func["args"] = []
            for name in func_def["args"]:
                type = func_def["var_types"][name]
                func["args"].append({"name" : name, "type" : type})
        funcs.append(func)
    return funcs

instrs = gen_var_defs(prog.get("var_types"), prog.get("var_inits"))

p = {"functions" : gen_func_defs(prog.get("func_defs"))}
p["functions"].append({"name" : "main", "instrs" : instrs})
json.dump(p, sys.stdout, indent=4)

