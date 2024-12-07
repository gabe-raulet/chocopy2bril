class VarDecls(object):

    def __init__(self, types, inits):
        self.types = types
        self.inits = inits

    @classmethod
    def from_var_defs(cls, var_defs):
        types, inits = {}, {}
        for var_def in var_defs:
            types[var_def.name] = var_def.type
            inits[var_def.name] = var_def.init
        return cls(types, inits)

    def __repr__(self):
        return f"VarDecls(types={self.types}, inits={self.inits})"

    def get_type(self, name):
        return self.types[name]

    def get_init(self, name):
        return self.inits[name]

    def add_var(self, name, type):
        self.types[name] = type

    def get_instrs(self):
        instrs = []
        for name, init in self.inits.items():
            instrs.append({"dest" : name, "op" : "const", "value" : init, "type" : self.types[name]})
        return instrs

class Scope(object):

    def __init__(self, var_decls, func_defs=[]):
        self.reg = 0
        self.types = {}
        for name in var_decls.types:
            self.types[name] = var_decls.get_type(name)
        for func_def in func_defs:
            if func_def.type:
                self.types[func_def.name] = func_def.type

    def get_type(self, name):
        return self.types.get(name)

    def next_reg(self):
        reg = f"r{self.reg}"
        self.reg += 1
        return reg

class Ast(object):
    pass

class Program(Ast):

    def __init__(self, var_defs, func_defs, body):
        self.var_decls = VarDecls.from_var_defs(var_defs)
        self.func_defs = func_defs
        self.body = body

    def __repr__(self):
        return f"Program(func_defs={self.func_defs}, body={self.body})"

    def get_main_func(self):
        instrs = self.var_decls.get_instrs()
        scope = Scope(self.var_decls, self.func_defs)
        for stmt in self.body:
            instrs += stmt.get_instrs(scope)
        return {"name" : "main", "instrs" : instrs}

    def get_bril(self):
        funcs = [self.get_main_func()]
        for func_def in self.func_defs:
            funcs.append(func_def.get_bril())
        prog = {"functions" : funcs}
        return prog

class TypedVar(Ast):

    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __repr__(self):
        return f"TypedVar(name={self.name}, type={self.type})"

class VarDef(Ast):

    def __init__(self, typed_var, literal):
        assert typed_var.type == literal.type
        self.name = typed_var.name
        self.type = typed_var.type
        self.init = literal.value

    def __repr__(self):
        return f"VarDef(name={self.name}, type={self.type}, init={self.init})"

class FuncDef(Ast):

    def __init__(self, name, body, var_defs, params, type):
        self.name = name
        self.body = body
        self.var_decls = VarDecls.from_var_defs(var_defs)
        self.type = type
        self.params = []
        for param in params:
            self.params.append(param.name)
            self.var_decls.add_var(param.name, param.type)

    def __repr__(self):
        return f"FuncDef(name={self.name}, params={self.params}, type={self.type})"

    def get_bril(self):
        instrs = self.var_decls.get_instrs()
        scope = Scope(self.var_decls)
        for stmt in self.body:
            instrs += stmt.get_instrs(scope)
        func = {"name" : self.name, "instrs" : instrs}
        if self.type: func["type"] = self.type
        if self.params:
            args = []
            for name in self.params:
                args.append({"name" : name, "type" : self.var_decls.get_type(name)})
            func["args"] = args
        return func

class Stmt(Ast):
    pass

class PassStmt(Stmt):

    def __init__(self):
        pass

    def __repr__(self):
        return "PassStmt()"

    def get_instrs(self, scope):
        return [{"op" : "nop"}]

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
        type = self.expr.get_type(scope)
        instrs.append({"op" : "id", "dest" : self.dest, "type" : type, "args" : [arg]})
        return instrs

class ExprStmt(Stmt):

    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"ExprStmt(expr={self.expr})"

    def get_instrs(self, scope):
        return self.expr.get_instrs(scope)

class Expr(Ast):
    pass

class Literal(Expr):

    def __init__(self, value, type):
        self.value = value
        self.type = type

    def __repr__(self):
        return f"Literal(value={self.value}, type={self.type})"

    def get_type(self, scope):
        return self.type

    def get_instrs(self, scope):
        dest = scope.next_reg()
        return [{"dest" : dest, "op" : "const", "type" : self.type, "value" : self.value}]

class IdExpr(Expr):

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"IdExpr(name={self.name})"

    def get_type(self, scope):
        return scope.get_type(self.name)

    def get_instrs(self, scope):
        type = self.get_type(scope)
        dest = scope.next_reg()
        return [{"dest" : dest, "op" : "id", "type" : type, "args" : [self.name]}]

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
        type = self.get_type(scope)
        dest = scope.next_reg()
        instrs.append({"dest" : dest, "op" : "call", "type" : type, "funcs" : [self.name], "args" : args})
        return instrs
