import sys
import json
from lexer import Token, TokenPattern, lex_text

class Register(object):

    def __init__(self):
        self.cur = 0

    def reset(self):
        self.cur = 0

    def next(self):
        name = f"_v{self.cur}"
        self.cur += 1
        return name

reg = Register()

class Ast(object):
    pass

class AstProgram(Ast):

    def __init__(self, var_defs, stmts):
        self.var_defs = var_defs
        self.stmts = stmts

    def __repr__(self):
        return f"var_defs={self.var_defs}\nstmts={self.stmts}"

    def get_code(self):
        instrs = []
        for var_def in self.var_defs: instrs.append(var_def.get_instr())
        for stmt in self.stmts: instrs += stmt.get_code()
        return instrs

class AstVarDef(Ast):

    def __init__(self, name, lit):
        self.id = name
        self.lit = lit

    def __repr__(self):
        return f"AstVarDef(id={self.id}, lit={self.lit})"

    def get_instr(self):
        return {"dest" : self.id, "type" : "int", "value" : self.literal, "op" : "const"}

class AstPrint(Ast):

    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"AstPrint({self.expr})"

    def get_code(self):
        global reg
        dest = reg.next()
        def_inst = {"dest" : dest, "type" : "int"}
        if isinstance(self.expr, AstLiteral):
            def_inst["op"] = "const"
            def_inst["value"] = self.expr.lit
        elif isinstance(self.expr, AstVariable):
            def_inst["op"] = "id"
            def_inst["args"] = [self.expr.id]
        else:
            raise Exception("Invalid expression for print")
        print_inst = {"op" : "print", "args" : [dest]}
        return [def_inst, print_inst]

class AstLiteral(Ast):

    def __init__(self, lit):
        self.lit = lit

    def __repr__(self):
        return f"AstLiteral({self.lit})"

class AstVariable(Ast):

    def __init__(self, name):
        self.id = name

    def __repr__(self):
        return f"AstVariable({self.id})"

class Parser(object):

    def __init__(self, tokens):
        self.tokens = tokens
        self.size = len(tokens)
        self.pos = 0

    def error(self, msg=None):
        raise Exception("Syntax error" if not msg else f"Syntax error: {msg}")

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
        if matchee == token: self.advance()
        else: self.error()
        return matchee

    def match_newline(self):
        self.match("NEWLINE")

    def get_program(self):
        var_defs = self.get_var_defs()
        stmts = self.get_stmts()
        return AstProgram(var_defs, stmts)

    def get_var_defs(self):
        var_defs = []
        while self.token() == Token.ID and self.token(1) == Token.COLON:
            var_defs.append(self.get_var_def())
        return var_defs

    def get_var_def(self):
        id_token = self.match(Token.ID)
        self.match(Token.COLON)
        type_token = self.match(Token.TYPE)
        assert type_token.value == "int" # TODO temporary
        self.match(Token.ASSIGN)
        lit_token = self.match(Token.NUM)
        self.match_newline()
        return AstVarDef(id_token.value, lit_token.value)

    def get_stmts(self):
        stmts = []
        while self.token(): stmts.append(self.get_stmt())
        return stmts

    def get_stmt(self):
        stmt = None
        if self.token() == Token.KEYWORD:
            if self.token().lexeme() == "print":
                self.match(Token.KEYWORD)
                self.match(Token.LPAREN)
                stmt = AstPrint(self.get_expr())
                self.match(Token.RPAREN)
            else:
                self.error("Only keyword implemented is print, currently") # TODO
        else:
            self.error("Only stmt implemented is AstPrint currently") # TODO
        self.match_newline()
        return stmt

    def get_expr(self):
        expr = None
        if self.token() == Token.NUM:
            result = self.match(Token.NUM)
            expr = AstLiteral(result.value)
        elif self.token() == Token.ID:
            result = self.match(Token.ID)
            expr = AstVariable(result.value)
        else:
            self.error()
        return expr

def read_text(fname):
    return open(fname).read()

#  if __name__ == "__main__":
    #  tokens = list(lex_text(sys.stdin.read()))
    #  parser = Parser(tokens)
    #  program = parser.get_program()
    #  func = {"name": "main", "instrs" : program.get_code()}
    #  prog = {"functions" : [func]}
    #  json.dump(prog, sys.stdout, indent=4)

tokens = list(lex_text(read_text("t4.py")))
parser = Parser(tokens)

