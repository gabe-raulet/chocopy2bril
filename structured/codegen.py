import sys
import json
from parser import del_nulls

def code_var_defs(types, inits):
    instrs = []
    if not types or not inits: return instrs
    for name in inits:
        instrs.append({"op" : "const", "dest" : name, "type" : types[name], "value" : inits[name]["literal"]})
    return instrs

def code_func_def(func):
    bril = {}
    bril["name"] = func["name"]
    bril["instrs"] = code_var_defs(func.get("types"), func.get("inits"))
    if not bril["instrs"]: bril["instrs"].append({"op" : "nop"})
    bril["type"] = func.get("type")
    bril["args"] = [{"name" : arg, "type" : func["types"][arg]} for arg in func.get("args", [])]
    return del_nulls(bril)

def code_program(program):
    decls = program["decls"]
    #  stmts = program["stmts"]
    funcs = [code_func_def(func) for name, func in decls.get("funcs", {}).items()]
    return {"functions" : funcs}

#  program = json.load(open("prog.json"))
#  json.dump(code_program(program), sys.stdout, indent=4)

#  decls = program["decls"]
#  stmts = program["stmts"]

#  funcs = decls["funcs"]
#  inits = decls["inits"]
#  types = decls["types"]

#  func = funcs["func1"]

if __name__ == "__main__":
    program = json.load(sys.stdin)
    json.dump(code_program(program), sys.stdout, indent=4)
