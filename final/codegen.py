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
        typed_var = var_def["typed_var"]
        name = typed_var["id"]
        type = typed_var["type"]
        init = read_literal(var_def["literal"], type)
        types[name] = type
        inits[name] = init
    return types, inits

def code_var_defs(types, inits):
    instrs = []
    for name in inits:
        init = inits[name]
        type = types[name]
        instrs.append({"op" : "const", "dest" : name, "type" : type, "value" : init})
    return instrs

def code_print(expr, types, inits):
    instrs = []
    if isinstance(expr, str):
        assert expr in types
        type = types[expr]
        instrs.append({"op" : "print", "args" : [expr]})
    else:
        assert "value" in expr and "type" in expr
        instrs.append({"op" : "const", "dest" : "tmp", "type" : expr["type"], "value" : expr["value"]})
        instrs.append({"op" : "print", "args" : ["tmp"]})
    return instrs

def code_assign(dest, expr, types, inits):
    instrs = []
    if isinstance(expr, str):
        assert expr in types
        assert types[expr] == types[dest]
        instrs.append({"op" : "id", "dest" : dest, "type" : types[dest], "args" : [expr]})
    else:
        assert "value" in expr
        value = read_literal(expr, types[dest])
        instrs.append({"op" : "const", "dest" : dest, "type" : types[dest], "value" : value})
    return instrs

def code_stmt(stmt, types, inits):
    if stmt.get("stmt") == "print":
        return code_print(stmt["expr"], types, inits)
    elif stmt.get("stmt") == "assign":
        return code_assign(stmt["dest"], stmt["expr"], types, inits)
    else:
        raise Exception()

def code_stmts(stmts, types, inits):
    instrs = []
    for stmt in stmts: instrs += code_stmt(stmt, types, inits)
    return instrs

#  tokens = list(lex_text(open("prog.py").read()))
#  parser = Parser(tokens)
#  program = parser.get_program()

#  var_defs = program.get("var_defs", [])
#  stmts = program.get("stmts", [])

#  types, inits = read_var_defs(var_defs)
#  instrs = code_var_defs(types, inits)
#  instrs += code_stmts(stmts, types, inits)

if __name__ == "__main__":
    tokens = list(lex_text(sys.stdin.read()))
    parser = Parser(tokens)
    program = parser.get_program()
    var_defs = program.get("var_defs", [])
    stmts = program.get("stmts", [])
    types, inits = read_var_defs(var_defs)
    instrs = code_var_defs(types, inits)
    instrs += code_stmts(stmts, types, inits)
    prog = {"functions" : [{"name" : "main", "instrs" : instrs}]}
    json.dump(prog, sys.stdout, indent=4)

"""
    program = {
        "func_defs"? : List[func_def],
         "var_defs"? : List[var_def],
            "stmts"? : List[stmt]
        }

    var_def = {
        "typed_var" : typed_var,
          "literal" : literal
        }

    print_stmt = {
            "stmt" : "print",
            "expr" : expr
        }

    assign_stmt = {
            "stmt" : "assign",
            "dest" : ID,
            "expr" : expr
        }

    typed_var = {
              "id" : ID,
            "type" : type
        }

    literal = {
            "value" : None | BOOL | NUM,
            "type"? : type
        }
"""

