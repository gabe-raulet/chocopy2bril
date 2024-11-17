import ast

program = "".join(line for line in open("ex2.py", "r"))
tree = ast.parse(program)

with open("ex2.tree", "w") as f:
    f.write(ast.dump(ast.parse(program), indent=4))
