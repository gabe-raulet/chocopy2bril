import sys
import json
from lexer import *

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

    def match_indent(self):
        self.match("INDENT")

    def match_dedent(self):
        self.match("DEDENT")

    def not_done(self):
        return self.token() is not None

    def matches_keyword(self, word):
        return self.not_done() and self.token().matches(Token.KEYWORD) and self.token().value == word

    def matches_typed_var(self):
        return self.not_done() and self.token().matches(Token.ID) and self.token(1).matches(Token.COLON)

    def matches_func_def(self):
        return self.not_done() and self.matches_keyword("def") and self.token(1).matches(Token.ID)

    def matches_func_call(self):
        return self.not_done() and self.token().matches(Token.ID) and self.token(1).matches(Token.LPAREN)

    def matches_assign(self):
        return self.not_done() and self.token().matches(Token.ID) and self.token(1).matches(Token.ASSIGN)

    def get_typed_var(self):
        typed_var = {} # {name -> str; type -> "int|bool"}
        assert self.matches_typed_var()
        typed_var["name"] = self.match(Token.ID).value
        self.match(Token.COLON)
        typed_var["type"] = self.match(Token.TYPE).value
        return typed_var

    def get_var_def(self):
        var_def = {} # {typed_var -> dict; init -> NUM|BOOL}
        assert self.matches_typed_var()
        typed_var = self.get_typed_var()
        var_def["typed_var"] = typed_var
        self.match(Token.ASSIGN)
        if self.matches_keyword("None"):
            self.advance()
            var_def["init"] = None
        elif typed_var["type"] == "int":
            var_def["init"] = self.match(Token.NUM).value
        elif typed_var["type"] == "bool":
            var_def["init"] = self.match(Token.BOOL).value
        else:
            self.error()
        self.match_newline()
        return var_def

    def get_func_def(self):
        func_def = {} # {name -> str; typed_vars -> list; var_defs -> list; stmts -> list; ... rtype -> "int|bool"}
        assert self.matches_keyword("def")
        self.match(Token.KEYWORD)
        func_def["name"] = self.match(Token.ID).value
        self.match(Token.LPAREN)
        func_def["typed_vars"] = []
        if self.matches_typed_var():
            func_def["typed_vars"].append(self.get_typed_var())
            while self.token().matches(Token.COMMA):
                self.match(Token.COMMA)
                func_def["typed_vars"].append(self.get_typed_var())
        self.match(Token.RPAREN)
        if self.token().matches(Token.ARROW):
            self.match(Token.ARROW)
            func_def["rtype"] = self.match(Token.TYPE).value
        self.match(Token.COLON)
        self.match_newline()
        self.match_indent()
        func_def["var_defs"] = []
        while self.matches_typed_var():
            var_def = self.get_var_def()
            func_def["var_defs"].append(var_def)
            func_def["typed_vars"].append(var_def["typed_var"])
        func_def["stmts"] = []
        while not self.token().matches("DEDENT"):
            func_def["stmts"].append(self.get_stmt())
        self.match_dedent()
        if not bool(func_def["typed_vars"]): del func_def["typed_vars"]
        if not bool(func_def["var_defs"]): del func_def["var_defs"]
        return func_def

    def get_func_call(self):
        assert self.matches_func_call()
        stmt = {"op" : "call"}
        stmt["name"] = self.match(Token.ID).value
        stmt["args"] = []
        if not self.token().matches(Token.RPAREN):
            stmt["args"].append(self.get_expr())
            while self.token().matches(Token.COMMA):
                self.match(Token.COMMA)
                stmt["args"].append(self.get_expr())
        self.match(Token.RPAREN)
        if not bool(stmt["args"]): del stmt["args"]
        return stmt

    def get_assign(self):
        stmt = {"op" : "assign"}
        assert self.matches_assign()
        stmt["dest"] = self.match(Token.ID).value
        stmt["expr"] = self.get_expr()
        return stmt

    def get_print(self):
        stmt = {"op" : "print"}
        assert self.matches_keyword("print")
        self.match(Token.KEYWORD)
        self.match(Token.LPAREN)
        stmt["expr"] = self.get_expr()
        self.match(Token.RPAREN)
        return stmt

    def get_return(self):
        stmt = {"op" : "ret"}
        assert self.matches_keyword("return")
        self.match(Token.KEYWORD)
        stmt["expr"] = self.get_expr()
        return stmt

    def get_expr(self):
        if self.matches_func_call():
            return self.get_func_call()
        elif self.token().matches(Token.ID):
            name = self.match(Token.ID).value
            return {"name" : name}
        elif self.token().matches(Token.NUM):
            literal = self.match(Token.NUM).value
            return {"literal" : literal, "type" : "int"}
        elif self.token().matches(Token.BOOL):
            literal = self.match(Token.BOOL).value
            return {"literal" : literal, "type" : "bool"}
        else:
            self.error()
        return stmt

    def get_stmt(self):
        stmt = None
        if self.matches_keyword("print"):
            stmt = self.get_print()
        elif self.matches_keyword("return"):
            stmt = self.get_return()
        elif self.matches_assign():
            stmt = self.get_assign()
        else:
            stmt = self.get_expr()
        self.match_newline()
        return stmt

    def parse(self):

        program = {"var_defs" : [], "func_defs" : [], "stmts" : []}

        while True:
            if self.matches_typed_var(): program["var_defs"].append(self.get_var_def())
            elif self.matches_func_def(): program["func_defs"].append(self.get_func_def())
            else: break

        while self.not_done(): program["stmts"].append(self.get_stmt())

        if not bool(program["var_defs"]): del program["var_defs"]
        if not bool(program["func_defs"]): del program["func_defs"]
        if not bool(program["stmts"]): del program["stmts"]

        return program

if __name__ == "__main__":
    text = sys.stdin.read()
    tokens = list(lex_text(text))
    parser = Parser(tokens)
    program = parser.parse()
    json.dump(program, sys.stdout, indent=4)

#  text = open("prog.py").read()
#  tokens = list(lex_text(text))
#  parser = Parser(tokens)
#  program = parser.parse()
