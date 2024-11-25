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
        return self.var_defs # TODO: temporary

class AstVarDef(Ast):

    def __init__(self, var_id, var_type, literal):
        self.id = var_id
        self.type = var_type
        self.literal = literal

    def __repr__(self):
        return f"AstVarDef(id={self.id}, type={self.type}, literal={self.literal})"

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
        if self.pos + 1 < self.size:
            self.pos += 1

    def match(self, token):
        matchee = self.token()
        if matchee == token: self.advance()
        else: self.error()
        return matchee

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
        else:
            self.error("TODO: implement BOOL and STR token")
        self.match("NEWLINE")
        return AstVarDef(id_token.value, type_token.value, lit_token.value)

if __name__ == "__main__":
    tokens = list(lex_text(open("t3.py").read()))
    parser = Parser(tokens)
    var_defs = parser.get_var_defs()
