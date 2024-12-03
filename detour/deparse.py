import sys
import json

def decompile_var_defs(var_defs):
    lines = []
    for var_def in var_defs:
        name = var_def["name"]
        type = var_def["type"]
        init = var_def["init"]
        lines.append(f"{name}: {type} = {init}\n")
    return lines

def decompile(program):
    lines = decompile_var_defs(program.get("var_defs", []))
    return "".join(lines)

if __name__ == "__main__":
    program = json.load(sys.stdin)
    text = decompile(program)
    print(text)
