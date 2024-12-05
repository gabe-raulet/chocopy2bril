import sys
import json
from parser import del_nulls

def get_expr_type(expr, types):
    if "literal" in expr: return expr["type"]
    elif "identifier" in expr: return types[expr["identifier"]]
    else: raise Exception()

def get_literal_value(type, literal):
    if literal["literal"]: return literal["literal"]
    elif type == "int": return 0
    else: return False

def code_var_defs(types, inits):
    instrs = []
    if not types or not inits: return instrs
    for name in inits:
        value = get_literal_value(types[name], inits[name])
        instrs.append({"op" : "const", "dest" : name, "type" : types[name], "value" : get_literal_value(types[name], inits[name])})
    return instrs

def code_func_def(func):
    bril = {}
    bril["name"] = func["name"]
    bril["instrs"] = code_var_defs(func.get("types"), func.get("inits"))
    if not bril["instrs"]: bril["instrs"].append({"op" : "nop"})
    bril["type"] = func.get("type")
    bril["args"] = [{"name" : arg, "type" : func["types"][arg]} for arg in func.get("args", [])]
    return del_nulls(bril)

def code_expr(expr, types):
    instrs = []
    type = get_expr_type(expr, types)
    if "literal" in expr:
        instrs.append({"op" : "const", "dest" : "tmp", "type" : type, "value" : expr["literal"]})
    elif "identifier" in expr:
        instrs.append({"op" : "id", "dest" : "tmp", "type" : type, "args" : [expr["identifier"]]})
    else:
        raise Exception()
    return instrs

def code_print(expr, types):
    instrs = code_expr(expr, types)
    instrs.append({"op" : "print", "args" : [instrs[-1]["dest"]]})
    return instrs

def code_stmt(stmt, types):
    if stmt["stmt"] == "print": return code_print(stmt["expr"], types)
    elif stmt["stmt"] == "assign": return code_assign(stmt["expr"], stmt["dest"], types)
    else: raise Exception()

def code_program(program):
    decls = program["decls"]
    stmts = program["stmts"]
    funcs = [code_func_def(func) for name, func in decls.get("funcs", {}).items()]
    instrs = code_var_defs(decls.get("types"), decls.get("inits"))
    for stmt in stmts: instrs += code_stmt(stmt, decls.get("types"))
    funcs.append({"name" : "main", "instrs" : instrs})
    return {"functions" : funcs}

if __name__ == "__main__":
    program = json.load(sys.stdin)
    json.dump(code_program(program), sys.stdout, indent=4)
