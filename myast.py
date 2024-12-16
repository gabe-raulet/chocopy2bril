class Ast(object):
    pass

class TypedVar(Ast):

    def __init__(self, name: str, type: str):
        self.name = name
        self.type = type

    def __repr__(self):
        return f"TypedVar(name={self.name}, type={self.type})"

class Expr(Ast):
    pass

class IdExpr(Expr):

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"IdExpr(name={self.name})"

    def get_type(self, scope):
        return scope.get_type(self.name)

    def get_instrs(self, scope):
        dest = scope.next_reg()
        return [{"dest" : dest, "op" : "id", "type" : self.get_type(scope), "args" : [self.name]}]

class CallExpr(Expr):

    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"CallExpr(name={self.name}, args={self.args})"

    def get_type(self, scope):
        return scope.get_type(self.name)

    def get_instrs(self, scope):
        args, instrs = [], []
        for arg in self.args:
            instrs += arg.get_instrs(scope)
            args.append(instrs[-1]["dest"])

        instrs.append({"op" : "call", "funcs" : [self.name], "args" : args})

        type = self.get_type(scope)
        if type:
            dest = scope.next_reg()
            instrs[-1]["dest"] = dest
            instrs[-1]["type"] = type

        return instrs

class BinOpExpr(Expr):

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinOpExpr(op={self.op}, left={self.left}, right={self.right})"

    def get_type(self, scope):
        lhs = self.left.get_type(scope)
        rhs = self.right.get_type(scope)
        if self.op in {"ADD", "SUB", "MUL", "DIV", "MOD"}:
            assert lhs == "int" and rhs == "int"
            return "int"
        elif self.op in {"LT", "GT", "LE", "GE"}:
            assert lhs == "int" and rhs == "int"
            return "bool"
        elif self.op in {"EQ", "NE"}:
            assert lhs == rhs
            return "bool"
        elif self.op in {"AND", "OR"}:
            assert lhs == "bool" and rhs == "bool"
            return "bool"
        else:
            raise Exception()

    @staticmethod
    def traverse(node, scope, instrs, stack):
        if isinstance(node, BinOpExpr):
            BinOpExpr.traverse(node.left, scope, instrs, stack)
            BinOpExpr.traverse(node.right, scope, instrs, stack)
            rhs = stack.pop()
            lhs = stack.pop()
            dest = scope.next_reg()
            op = node.op.lower()
            ltype = node.left.get_type(scope)
            rtype = node.right.get_type(scope)
            if op == "mod":
                assert ltype == "int" and rtype == "int"
                instrs.append({"dest" : dest, "op" : "div", "type" : "int", "args" : [lhs, rhs]})
                instrs.append({"dest" : dest, "op" : "mul", "type" : "int", "args" : [dest, rhs]})
                instrs.append({"dest" : dest, "op" : "sub", "type" : "int", "args" : [lhs, dest]})
            elif op in {"lt", "gt", "le", "ge"}:
                assert ltype == "int" and rtype == "int"
                instrs.append({"dest" : dest, "op" : op, "type" : "bool", "args" : [lhs, rhs]})
            elif op in {"eq", "ne"}:
                assert ltype == "int" and rtype == "int" # TODO: implement version that works for bools as well
                instrs.append({"dest" : dest, "op" : "eq", "type" : "bool", "args" : [lhs, rhs]})
                if op == "ne":
                    instrs.append({"dest" : dest, "op" : "not", "type" : "bool", "args" : [dest]})
            elif op  in {"or", "and"}:
                assert ltype == "bool" and rtype == "bool"
                instrs.append({"dest" : dest, "op" : op, "type" : "bool", "args" : [lhs, rhs]})
            elif op in {"add", "sub", "mul", "div"}:
                assert ltype == "int" and rtype == "int"
                instrs.append({"dest" : dest, "op" : op, "type" : "int", "args" : [lhs, rhs]})
            else:
                raise Exception()
            stack.append(dest)
        else:
            instrs += node.get_instrs(scope)
            dest = instrs[-1]["dest"]
            stack.append(dest)

    def get_instrs(self, scope):
        instrs, stack = [], []
        BinOpExpr.traverse(self, scope, instrs, stack)
        return instrs

class UnOpExpr(Expr):

    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def __repr__(self):
        return f"UnOpExpr(op={self.op}, expr={self.expr})"

    def get_type(self, scope):
        return self.expr.get_type(scope)

    def get_instrs(self, scope):
        instrs = self.expr.get_instrs(scope)
        dest = instrs[-1]["dest"]
        op = self.op.lower()
        if op == "not":
            assert self.get_type(scope) == "bool"
            instrs.append({"op" : self.op.lower(), "dest" : dest, "type" : "bool", "args" : [dest]})
        else:
            assert op == "sub"
            tmp = scope.next_reg()
            instrs.append({"op" : "const", "dest" : tmp, "type" : "int", "value" : -1})
            instrs.append({"op" : "mul", "dest" : dest, "type" : "int", "args" : [dest, tmp]})
        return instrs

class Literal(Expr):

    def __init__(self, value: int | bool, type: str):
        self.value = value
        self.type = type

    def __repr__(self):
        return f"Literal(value={self.value}, type={self.type})"

    def get_instrs(self, scope):
        dest = scope.next_reg()
        return [{"dest" : dest, "op" : "const", "type" : self.type, "value" : self.value}]

    def get_type(self, scope):
        return self.type

class Stmt(Ast):
    pass

class ForStmt(Stmt):

    def __init__(self, iter_name: str, bounds: list[int], block: list[Stmt]):
        self.iter_name = iter_name
        self.bounds = bounds
        self.block = block

    def __repr__(self):
        return f"ForStmt(iter_name={self.iter_name}, bounds={self.bounds}, block={self.block})"

    def get_instrs(self, scope):

        label = scope.next_label()
        entry_label = f"entry.{label}"
        body_label = f"body.{label}"
        exit_label = f"exit.{label}"

        scope.type_map[self.iter_name] = "int"

        instrs = []
        term = None

        if len(self.bounds) == 1:
            instrs.append({"op" : "const", "dest" : self.iter_name, "type" : "int", "value" : 0})
            term = self.bounds[0]
        else:
            instrs.append({"op" : "const", "dest" : self.iter_name, "type" : "int", "value" : self.bounds[0]})
            term = self.bounds[1]

        term_name = scope.next_reg()
        instrs.append({"op" : "const", "dest" : term_name, "type" : "int", "value" : term})

        inc_name = scope.next_reg()
        instrs.append({"op" : "const", "dest" : inc_name, "type" : "int", "value" : 1})

        instrs.append({"label" : entry_label})
        cond = scope.next_reg()
        instrs.append({"op" : "lt", "dest" : cond, "type" : "bool", "args" : [self.iter_name, term_name]})
        instrs.append({"op" : "br", "labels" : [body_label, exit_label], "args" : [cond]})

        instrs.append({"label" : body_label})
        for stmt in self.block: instrs += stmt.get_instrs(scope)
        instrs.append({"op" : "add", "dest" : self.iter_name, "type" : "int", "args" : [self.iter_name, inc_name]})
        instrs.append({"op" : "jmp", "labels" : [entry_label]})

        instrs.append({"label" : exit_label})
        return instrs

class WhileStmt(Stmt):

    def __init__(self, cond : Expr, block: list[Stmt]):
        self.cond = cond
        self.block = block

    def __repr__(self):
        return f"WhileStmt(cond={self.cond}, block={self.block})"

    def get_instrs(self, scope):

        label = scope.next_label()
        entry_label = f"entry.{label}"
        body_label = f"body.{label}"
        exit_label = f"exit.{label}"

        instrs = [{"label" : entry_label}]
        instrs += self.cond.get_instrs(scope)
        cond = instrs[-1]["dest"]
        instrs.append({"op" : "br", "labels" : [body_label, exit_label], "args" : [cond]})

        instrs.append({"label" : body_label})
        for stmt in self.block:
            instrs += stmt.get_instrs(scope)

        instrs.append({"op" : "jmp", "labels" : [entry_label]})
        instrs.append({"label" : exit_label})
        return instrs

class IfStmt(Stmt):

    def __init__(self, cond, if_block, elif_blocks, else_block):
        self.cond = cond
        self.if_block = if_block
        self.elif_blocks = elif_blocks
        self.else_block = else_block

    def __repr__(self):
        return f"IfStmt(cond={self.cond}, if_block={self.if_block}, elif_blocks={self.elif_blocks}, else_block={self.else_block})"

    def get_instrs(self, scope):
        label = scope.next_label()
        then_label = f"then.{label}"
        else_label = f"else.{label}"
        endif_label = f"endif.{label}"

        instrs = self.cond.get_instrs(scope)
        cond = instrs[-1]["dest"]

        instrs.append({"op" : "br", "labels" : [then_label, else_label], "args" : [cond]})
        instrs.append({"label" : then_label})

        for stmt in self.if_block: instrs += stmt.get_instrs(scope)
        instrs.append({"op" : "jmp", "labels" : [endif_label]})

        instrs.append({"label" : else_label})

        count = 1
        for lcond, lblock in self.elif_blocks:
            instrs += lcond.get_instrs(scope)
            cond = instrs[-1]["dest"]
            then_label = f"then.{label}.{count}"
            else_label = f"else.{label}.{count}"
            count += 1
            instrs.append({"op" : "br", "labels" : [then_label, else_label], "args" : [cond]})
            instrs.append({"label" : then_label})
            for stmt in lblock: instrs += stmt.get_instrs(scope)
            instrs.append({"op" : "jmp","labels" : [endif_label]})
            instrs.append({"label" : else_label})

        if self.else_block:
            for stmt in self.else_block:
                instrs += stmt.get_instrs(scope)

        instrs.append({"label" : endif_label})
        return instrs

class PassStmt(Stmt):

    def __repr__(self):
        return f"PassStmt()"

class PrintStmt(Stmt):

    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"PrintStmt(expr={self.expr})"

    def get_instrs(self, scope):
        instrs = self.expr.get_instrs(scope)
        arg = instrs[-1]["dest"]
        instrs.append({"op" : "print", "args" : [arg]})
        return instrs

class ReturnStmt(Stmt):

    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"ReturnStmt(expr={self.expr})"

    def get_instrs(self, scope):
        instrs = self.expr.get_instrs(scope)
        arg = instrs[-1]["dest"]
        instrs.append({"op" : "ret", "args" : [arg]})
        return instrs

class AssignStmt(Stmt):

    def __init__(self, dest, expr):
        self.dest = dest
        self.expr = expr

    def __repr__(self):
        return f"AssignStmt(dest={self.dest}, expr={self.expr})"

    def get_instrs(self, scope):
        instrs = self.expr.get_instrs(scope)
        arg = instrs[-1]["dest"]
        instrs.append({"op" : "id", "dest" : self.dest, "type" : self.expr.get_type(scope), "args" : [arg]})
        return instrs

class ExprStmt(Stmt):

    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"ExprStmt(expr={self.expr})"

    def get_instrs(self, scope):
        return self.expr.get_instrs(scope)

class VarDef(Ast):

    def __init__(self, typed_var: TypedVar, literal: Literal):
        assert typed_var.type == literal.type
        self.name = typed_var.name
        self.type = typed_var.type
        self.init = literal.value

    def __repr__(self):
        return f"VarDef(name={self.name}, type={self.type}, init={self.init})"

    def get_instr(self):
        return {"op" : "const", "dest" : self.name, "type" : self.type, "value" : self.init}

class Scope(object):

    def __init__(self, type_map):
        self.type_map = type_map
        self.reg = 1
        self.label = 1

    def get_type(self, name):
        return self.type_map.get(name)

    def next_reg(self):
        reg = f"v{self.reg}"
        self.reg += 1
        return reg

    def next_label(self):
        label = self.label
        self.label += 1
        return str(label)

class FuncBody(Ast):

    def __init__(self, var_defs: list[VarDef], stmts: list[Stmt]):
        self.var_defs = var_defs
        self.stmts = stmts

    def __repr__(self):
        return f"FuncBody(var_defs={self.var_defs}, stmts={self.stmts})"

    def get_instrs(self, params, body, func_types):

        type_map = {}
        instrs = []

        for typed_def in params:
            type_map[typed_def.name] = typed_def.type

        for name, type in func_types.items():
            type_map[name] = type

        for var_def in self.var_defs:
            type_map[var_def.name] = var_def.type
            instrs.append(var_def.get_instr())

        scope = Scope(type_map)

        for stmt in self.stmts:
            instrs += stmt.get_instrs(scope)

        return instrs

class FuncDef(Ast):

    def __init__(self, name: str, params: list[TypedVar], type: str, body: FuncBody):
        self.name = name
        self.params = params
        self.type = type
        self.body = body

    def __repr__(self):
        return f"FuncDef(name={self.name}, params={self.params}, type={self.type})"

    def get_instrs(self, func_types):
        instrs = self.body.get_instrs(self.params, self.body, func_types)
        return instrs

    def get_bril(self, func_types):
        func = {"name" : self.name, "instrs" : self.get_instrs(func_types)}
        if self.type: func["type"] = self.type
        if self.params:
            args = []
            for typed_var in self.params:
                args.append({"name" : typed_var.name, "type" : typed_var.type})
            func["args"] = args
        return func

class Program(Ast):

    def __init__(self, func_defs: list[FuncDef]):
        self.func_defs = func_defs

    def __repr__(self):
        return f"Program(func_defs={self.func_defs})"

    def get_bril(self):
        func_types = {func_def.name : func_def.type for func_def in self.func_defs}
        return {"functions" : [func_def.get_bril(func_types) for func_def in self.func_defs]}
