import sys
import json
from lexer import *
import pprint

def del_nulls(d):
    return {key : val for key, val in d.items() if bool(val)}

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

    def matches_newline(self):
        return self.not_done() and self.token().matches("NEWLINE")

    def matches_literal(self):
        return self.not_done() and (self.token().matches(Token.NUM) or self.token().matches(Token.BOOL) or self.matches_keyword("None"))

    def matches_keyword(self, word):
        return self.not_done() and self.token().matches(Token.KEYWORD) and self.token().value == word

    def matches_typed_var(self):
        return self.not_done() and self.token().matches(Token.ID) and self.token(1).matches(Token.COLON)

    def not_done(self):
        return self.token() is not None

    def get_typed_var(self):
        """
        typed_var ::= ID : type
        """
        assert self.matches_typed_var()
        name = self.match(Token.ID).value
        self.match(Token.COLON)
        type = self.match(Token.TYPE).value
        return {"id" : name, "type" : type}

    def get_literal(self):
        """
        literal ::= "None" | "False" | "True" | NUM
        """
        assert self.matches_literal()
        if self.matches_keyword("None"):
            self.match(Token.KEYWORD)
            return None
        elif self.token().matches(Token.NUM):
            return self.match(Token.NUM).value
        elif self.token().matches(Token.BOOL):
            return self.match(Token.BOOL).value
        else:
            self.error()

    def get_var_def(self):
        """
        var_def ::= typed_var = literal NEWLINE
        """
        assert self.matches_typed_var()
        typed_var = self.get_typed_var()
        self.match(Token.ASSIGN)
        literal = self.get_literal()
        self.match_newline()
        return {"id" : typed_var["id"], "type" : typed_var["type"], "literal" : literal}

    def get_decls(self):
        """
        decl ::= {var_def | func_def}
        """
        types, inits = {}, {}
        while True:
            if self.matches_typed_var():
                var_def = self.get_var_def()
                types[var_def["id"]] = var_def["type"]
                inits[var_def["id"]] = var_def["literal"]
            else:
                break
        return del_nulls({"types" : types, "inits" : inits})

    def get_program(self):
        return self.get_decls()

def get_pretty_json_str(d):
    json = pprint.pformat(d, compact=True)
    json = json.replace("'", '"').replace("False", "false").replace("True", "true").replace("None", "null")
    return json

if __name__ == "__main__":
    tokens = list(lex_text(sys.stdin.read()))
    parser = Parser(tokens)
    decls = parser.get_decls()
    sys.stdout.write(get_pretty_json_str(decls))
    sys.stdout.flush()
