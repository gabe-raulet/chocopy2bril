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

    def match_indent(self):
        self.match("INDENT")

    def match_dedent(self):
        self.match("DEDENT")

    def matches_newline(self):
        return self.not_done() and self.token().matches("NEWLINE")

    def matches_indent(self):
        return self.not_done() and self.token().matches("INDENT")

    def matches_dedent(self):
        return self.not_done() and self.token().matches("DEDENT")

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

    def matches_literal(self):
        return self.not_done() and (self.token().matches(Token.NUM) or self.token().matches(Token.BOOL) or self.matches_keyword("None"))

    def not_done(self):
        return self.token() is not None

    def get_typed_var(self):
        """
        typed_var ::= {id} : {type}
        """
        assert self.matches_typed_var()
        name = self.match(Token.ID).value
        self.match(Token.COLON)
        type = self.match(Token.TYPE).value
        return {"name" : name, "type" : type}

    def get_literal(self):
        """
        literal ::= NUM | ID | None
        """
        assert self.matches_literal()
        literal = None
        if self.matches_keyword("None"):
            self.match(Token.KEYWORD)
            literal = {"literal" : None}
        elif self.token().matches(Token.NUM):
            value = self.match(Token.NUM).value
            literal = {"literal" : value, "type" : "int"}
        elif self.token().matches(Token.BOOL):
            value = self.match(Token.BOOL).value
            literal = {"literal" : value, "type" : "bool"}
        else:
            self.error()
        return literal

    def get_decls(self):
        types, inits, funcs = {}, {}, {}
        while True:
            if self.matches_typed_var():
                typed_var = self.get_typed_var()
                name = typed_var["name"]
                type = typed_var["type"]
                self.match(Token.ASSIGN)
                init = self.get_literal()
                self.match_newline()
                types[name] = type
                inits[name] = init
            elif self.matches_func_def():
                func_def = self.get_func_def()
                name = func_def["name"]
                funcs[name] = func_def
            else:
                break
        return del_nulls({"types" : types, "inits" : inits, "funcs" : funcs})

    def get_func_def(self):
        assert self.matches_keyword("def")
        self.match(Token.KEYWORD)
        func_name = self.match(Token.ID).value
        self.match(Token.LPAREN)
        types = {}
        args = []
        if self.matches_typed_var():
            typed_var = self.get_typed_var()
            name = typed_var["name"]
            type = typed_var["type"]
            args.append(name)
            types[name] = type
            while self.token().matches(Token.COMMA):
                self.match(Token.COMMA)
                typed_var = self.get_typed_var()
                name = typed_var["name"]
                type = typed_var["type"]
                args.append(name)
                types[name] = type
        self.match(Token.RPAREN)
        type = None
        if self.token().matches(Token.ARROW):
            self.match(Token.ARROW)
            type = self.match(Token.TYPE).value
        self.match(Token.COLON)
        self.match_newline()
        self.match_indent()
        decls = self.get_decls()
        assert "funcs" not in decls
        self.match_dedent()
        if "types" in decls:
            for var_name, var_type in decls["types"].items():
                types[var_name] = var_type
        inits = decls.get("inits")
        return del_nulls({"name" : func_name, "args" : args, "types" : types, "inits" : inits, "type" : type})

    def get_stmts(self):
        pass

def get_pretty_json_str(d):
    json = pprint.pformat(d, compact=True)
    json = json.replace("'", '"').replace("False", "false").replace("True", "true").replace("None", "null")
    return json

if __name__ == "__main__":
    tokens = list(lex_text(sys.stdin.read()))
    parser = Parser(tokens)
    program = parser.get_decls()
    sys.stdout.write(get_pretty_json_str(program))
    sys.stdout.flush()
