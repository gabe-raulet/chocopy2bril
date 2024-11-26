import re
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

    def get_instrs(self, func):
        instrs, dest = self.expr.get_instrs(func)
        instrs.append({"op" : "print", "args" : [dest]})
        return instrs

class AstAssign(Ast):

    def __init__(self, target, expr):
        self.target = target
        self.expr = expr

    def __repr__(self):
        return f"AstAssign(target={self.target}, expr={self.expr})"

    def get_instrs(self, func):
        instrs, dest = self.expr.get_instrs(func)
        instrs.append({"dest" : self.target.name, "type" : self.target.type, "op" : "id", "args" : [dest]})
        return instrs

class AstLiteral(Ast):

    def __init__(self, lit):
        self.lit = lit
        self.type = "int"

    def __repr__(self):
        return f"AstLiteral(lit={self.lit}, type={self.type})"

    def get_instrs(self, func):
        dest = func.next_reg()
        return [{"dest" : dest, "type" : self.type, "op" : "const", "value" : self.lit}], dest

class AstVariable(Ast):

    def __init__(self, name):
        self.name = name
        self.type = "int"

    def __repr__(self):
        return f"AstVariable(name={self.name}, type={self.type})"

    def get_instrs(self, func):
        dest = func.next_reg()
        return [{"dest" : dest, "type" : self.type, "op" : "id", "args" : [self.name]}], dest

class AstVarDef(Ast):

    def __init__(self, var, lit):
        m_obj = re.match(r"r[0-9]+", var.name)
        if m_obj and m_obj.group() == var.name: raise Exception("Can't use register names as variables")
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

    def __repr__(self):
        return f"AstBinOp(op={self.op}, left={self.left}, right={self.right})"

class Function(object):

    def __init__(self, name="main"):
        self.name = name
        self.reg = 0
        self.vars = []
        self.stmts = []

    def next_reg(self):
        reg = f"r{self.reg}"
        self.reg += 1
        return reg

    def get_instrs(self):
        instrs = []
        for var in self.vars: instrs.append(var.get_instr())
        for stmt in self.stmts: instrs += stmt.get_instrs(self)
        return {"name" : self.name, "instrs" : instrs}

class Program(object):

    def __init__(self):
        self.funcs = []

    def get_prog(self):
        return {"functions" : [func.get_instrs() for func in self.funcs]}

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
        elif self.token().matches(Token.ID) and self.token(1).matches(Token.ASSIGN):
            target = AstVariable(self.match(Token.ID).value)
            self.match(Token.ASSIGN)
            stmt = AstAssign(target, self.get_expr())
        else:
            self.error()
        self.match_newline()
        return stmt

    def get_expr(self):
        expr = self.get_term()
        while self.token().matches([Token.ADD, Token.SUB]):
            op = self.token().name
            self.advance()
            expr = AstBinOp(op=op, left=expr, right=self.get_term())
        return expr

    def get_term(self):
        term = self.get_factor()
        while self.token().matches([Token.MUL, Token.DIV]):
            op = self.token().name
            self.advance()
            term = AstBinOp(op=op, left=term, right=self.get_factor())
        return term

    def get_factor(self):
        if self.token().matches(Token.LPAREN):
            self.match(Token.LPAREN)
            factor = self.get_expr()
            self.match(Token.RPAREN)
            return factor
        elif self.token().matches(Token.NUM):
            return AstLiteral(self.match(Token.NUM).value)
        elif self.token().matches(Token.ID):
            return AstVariable(self.match(Token.ID).value)
        else:
            self.error()

if __name__ == "__main__":
    tokens = [Token.from_dict(token) for token in json.load(sys.stdin)]
    parser = Parser(tokens)
    prog = parser.parse()
    json.dump(prog.get_prog(), sys.stdout, indent=4)
