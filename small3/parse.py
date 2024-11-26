import sys
import json
from lexer import Token

class Ast(object):
    pass

class AstPrint(Ast):

    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"AstPrint({self.expr})"

    def get_instrs(self):
        return [{"op" : "print", "args" : [self.expr.name]}]

class AstAssign(Ast):

    def __init__(self, target, expr):
        self.target = target
        self.expr = expr

class AstLiteral(Ast):

    def __init__(self, lit):
        self.lit = lit
        self.type = "int"

    def __repr__(self):
        return f"AstLiteral(lit={self.lit}, type={self.type})"

class AstVariable(Ast):

    def __init__(self, name):
        self.name = name
        self.type = "int"

    def __repr__(self):
        return f"AstVariable(name={self.name}, type={self.type})"

class AstVarDef(Ast):

    def __init__(self, var, lit):
        assert var.type == lit.type
        self.var = var
        self.lit = lit

    def __repr__(self):
        return f"AstVarDef({self.var}, {self.lit})"

    def get_instr(self):
        return {"dest" : self.var.name, "type" : self.var.type, "value" : self.lit.lit, "op" : "const"}

class AstBinOp(Ast):

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class Function(object):

    def __init__(self, name="main"):
        self.name = name
        self.reg = 0
        self.vars = []
        self.stmts = []

    def get_instrs(self):
        instrs = []
        for var in self.vars: instrs.append(var.get_instr())
        for stmt in self.stmts: instrs += stmt.get_instrs()
        return instrs

    def get_func(self):
        return {"name" : self.name, "instrs" : self.get_instrs()}

class Program(object):

    def __init__(self):
        self.funcs = []

    def get_prog(self):
        return {"functions" : [func.get_func() for func in self.funcs]}

class Parser(object):

    def __init__(self, tokens):
        self.tokens = tokens
        self.size = len(tokens)
        self.pos = 0

    def error(self, msg=""):
        if msg: msg = f": {msg}"
        raise Exception("Syntax error{msg}")

    def token(self, peek_amt=0):
        if self.pos + peek_amt < self.size:
            return self.tokens[self.pos + peek_amt]
        else:
            return None

    def advance(self):
        if self.pos < self.size:
            self.pos += 1

    def match(self, token):
        matchee = self.token()
        if matchee.matches(token): self.advance()
        else: self.error()
        return matchee

    def match_newline(self):
        self.match("NEWLINE")

    def get_var_defs(self):
        var_defs = []
        while self.token().matches(Token.ID) and self.token(1).matches(Token.COLON):
            var_name = self.match(Token.ID).value
            self.match(Token.COLON)
            var_type = self.match(Token.TYPE).value
            self.match(Token.ASSIGN)
            if var_type == "int":
                lit = self.match(Token.NUM).value
            else:
                self.error()
            self.match_newline()
            var_defs.append(AstVarDef(AstVariable(var_name), AstLiteral(lit)))
        return var_defs

    def parse(self):
        prog = Program()
        func = Function()
        func.vars = self.get_var_defs()
        func.stmts = self.get_stmts()
        prog.funcs.append(func)
        return prog

    def get_stmts(self):
        stmts = []
        while self.token(): stmts.append(self.get_stmt())
        return stmts

    def get_stmt(self):
        stmt = None
        if self.token().matches(Token.KEYWORD):
            if self.token().value == "print":
                self.match(Token.KEYWORD)
                self.match(Token.LPAREN)
                stmt = AstPrint(self.get_expr())
                self.match(Token.RPAREN)
            else:
                self.error()
        else:
            self.error()
        self.match_newline()
        return stmt

    def get_expr(self):
        name = self.match(Token.ID).value
        return AstVariable(name)

if __name__ == "__main__":
    tokens = [Token.from_dict(token) for token in json.load(sys.stdin)]
    parser = Parser(tokens)
    prog = parser.parse()
    json.dump(prog.get_prog(), sys.stdout, indent=4)
