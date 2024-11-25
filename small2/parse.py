import sys
import json
from lexer import Token, TokenPattern, lex_text

class Ast(object):
    pass

class AstProgram(Ast):

    def __init__(self, var_defs, stmts):
        self.var_defs = var_defs
        self.stmts = stmts

    def __repr__(self):
        return f"var_defs={self.var_defs}\nstmts={self.stmts}"

class AstVarDef(Ast):

    def __init__(self, var_id, var_type, literal):
        self.id = var_id
        self.type = var_type
        self.literal = literal

    def __repr__(self):
        return f"AstVarDef(id={self.id}, type={self.type}, literal={self.literal})"

class AstPrint(Ast):

    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"AstPrint({self.expr})"

class AstToken(Ast):

    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return f"AstToken({repr(self.token)})"

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
        self.match(Token.ASSIGN)
        if type_token.value == "int":
            lit_token = self.match(Token.NUM)
        elif type_token.value == "bool":
            lit_token = self.match(Token.BOOL)
        else:
            self.error() # TODO: str token if we want to do that eventually
        self.match("NEWLINE")
        return AstVarDef(id_token.value, type_token.value, lit_token.value)

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
                stmt = AstPrint(expr=self.get_expr())
                self.match(Token.RPAREN)
            else:
                self.error("Only keyword implemented is print") # TODO
        else:
            self.error("Only stmt implemented is AstPrint") # TODO
        self.match("NEWLINE")
        return stmt

    def get_expr(self):
        expr = None
        if self.token() == Token.NUM:
            expr = AstToken(self.match(Token.NUM))
        elif self.token() == Token.ID:
            expr = AstToken(self.match(Token.ID))
        else:
            self.error("only single token expressions implemented so far")
        return expr

if __name__ == "__main__":
    tokens = list(lex_text(open("t1.py").read()))
    parser = Parser(tokens)
    program = parser.get_program()
