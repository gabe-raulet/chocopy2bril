import sys
import json
from lexer import *
from parser import *
import pprint

def read_literal(literal, type):
    assert literal.get("type", type) == type
    if literal["value"] is None:
        return {"int" : 0, "bool" : False}[type]
    else:
        return literal["value"]

def read_var_defs(var_defs):
    types, inits = {}, {}
    for var_def in var_defs:
        name = var_def["typed_var"]["id"]
        types[name] = var_def["typed_var"]["type"]
        inits[name] = read_literal(var_def["literal"], types[name])
    return types, inits

def read_func_defs(func_defs):
    funcs = {}
    for func_def in func_defs:
        var_defs = func_def.get("var_defs", [])
        params = func_def.get("params", [])
        types, inits = read_var_defs(var_defs)
        args = []
        for typed_var in params:
            name = typed_var["id"]
            type = typed_var["type"]
            types[name] = type
            args.append(name)
        func = {"stmts" : func_def["stmts"]}
        if args: func["args"] = args
        if types: func["types"] = types
        if inits: func["inits"] = inits
        if "type" in func_def: func["type"] = func_def["type"]
        funcs[func_def["name"]] = func
    return funcs

tokens = list(lex_text(open("prog2.py").read()))
parser = Parser(tokens)
program = parser.get_program()

types, inits = read_var_defs(program.get("var_defs", []))
funcs = read_func_defs(program.get("func_defs", []))
