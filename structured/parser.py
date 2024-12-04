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

    def matches_assign_stmt(self):
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

    def get_expr(self):
        if self.matches_literal():
            return self.get_literal()
        elif self.token().matches(Token.ID):
            name = self.match(Token.ID).value
            return {"name" : name}
        else:
            self.error()

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

    def get_var_def(self):
        assert self.matches_typed_var()
        typed_var = self.get_typed_var()
        self.match(Token.ASSIGN)
        init = self.get_literal()
        self.match_newline()
        return {"name" : typed_var["name"], "type" : typed_var["type"], "init" : init}

    def get_decls(self):
        types, inits, funcs = {}, {}, {}
        while True:
            if self.matches_typed_var():
                var_def = self.get_var_def()
                types[var_def["name"]] = var_def["type"]
                inits[var_def["name"]] = var_def["init"]
            elif self.matches_func_def():
                func_def = self.get_func_def()
                funcs[func_def["name"]] = func_def
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
        stmts = self.get_func_stmts()
        assert "funcs" not in decls
        self.match_dedent()
        if "types" in decls:
            for var_name, var_type in decls["types"].items():
                types[var_name] = var_type
        inits = decls.get("inits")
        return del_nulls({"name" : func_name, "args" : args, "types" : types, "inits" : inits, "type" : type, "stmts" : stmts})

    #  * Expression statements
    #  * Assignment statements
    #  * Print statements (special to Bril)
    #  * Pass statement
    #  * Return statement

    def get_pass_stmt(self):
        assert self.matches_keyword("pass")
        stmt = {"stmt" : "pass"}
        self.match(Token.KEYWORD)
        return stmt

    def get_print_stmt(self):
        assert self.matches_keyword("print")
        stmt = {"stmt" : "print"}
        self.match(Token.KEYWORD)
        self.match(Token.LPAREN)
        stmt["expr"] = self.get_expr()
        self.match(Token.RPAREN)
        return stmt

    def get_return_stmt(self):
        assert self.matches_keyword("return")
        stmt = {"stmt" : "return"}
        self.match(Token.KEYWORD)
        stmt["expr"] = self.get_expr()
        return stmt

    def get_assign_stmt(self):
        assert self.matches_assign()
        stmt = {"stmt" : "assign"}
        stmt["dest"] = self.match(Token.ID).value
        self.match(Token.ASSIGN)
        stmt["expr"] = self.get_expr()
        return stmt

    def get_expr_stmt(self):
        stmt = {"stmt" : "expr"}
        stmt["expr"] = self.get_expr()
        return stmt

    def get_stmt(self):
        stmt = None
        if self.matches_keyword("pass"):
            stmt = self.get_pass_stmt()
        elif self.matches_keyword("print"):
            stmt = self.get_print_stmt()
        elif self.matches_keyword("return"):
            stmt = self.get_return_stmt()
        elif self.matches_assign_stmt():
            stmt = self.get_assign_stmt()
        else:
            stmt = self.get_expr_stmt()
        self.match_newline()
        return stmt

    def get_stmts(self):
        stmts = []
        while self.not_done(): stmts.append(self.get_stmt())
        return stmts

    def get_func_stmts(self):
        stmts = []
        while not self.matches_dedent(): stmts.append(self.get_stmt())
        return stmts

    def get_program(self):
        decls = self.get_decls()
        stmts = self.get_stmts()
        return {"decls" : decls, "stmts" : stmts}

def get_pretty_json_str(d):
    json = pprint.pformat(d, compact=True)
    json = json.replace("'", '"').replace("False", "false").replace("True", "true").replace("None", "null")
    return json

#  tokens = list(lex_text(open("prog.py").read()))
#  parser = Parser(tokens)
#  program = parser.get_program()

if __name__ == "__main__":
    tokens = list(lex_text(sys.stdin.read()))
    parser = Parser(tokens)
    program = parser.get_program()
    sys.stdout.write(get_pretty_json_str(program))
    sys.stdout.flush()
