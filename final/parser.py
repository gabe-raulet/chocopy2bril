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

    def not_done(self):
        return self.token() is not None

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

    def get_typed_var(self):
        assert self.matches_typed_var()
        name = self.get_identifier()
        self.match(Token.COLON)
        type = self.get_type()
        return {"id" : name, "type" : type}

    def matches_var_def(self):
        return self.matches_typed_var()

    def get_var_def(self):
        assert self.matches_var_def()
        typed_var = self.get_typed_var()
        self.match(Token.ASSIGN)
        literal = self.get_literal()
        self.match_newline()
        return {"typed_var" : typed_var, "literal" : literal}

    def matches_func_def(self):
        return self.not_done() and self.matches_keyword("def") and self.token(1).matches(Token.ID)

    def get_func_def(self):
        assert self.matches_func_def()
        self.match(Token.KEYWORD)
        name = self.match(Token.ID).value
        self.match(Token.LPAREN)
        params = []
        if self.matches_typed_var():
            params.append(self.get_typed_var())
            while self.token().matches(Token.COMMA):
                self.match(Token.COMMA)
                params.append(self.get_typed_var())
        self.match(Token.RPAREN)
        type = None
        if self.token().matches(Token.ARROW):
            self.match(Token.ARROW)
            type = self.get_type()
        self.match(Token.COLON)
        self.match_newline()
        self.match_indent()
        var_defs = []
        while self.matches_var_def():
            var_defs.append(self.get_var_def())
        stmts = self.get_func_stmts()
        assert len(stmts) >= 1
        self.match_dedent()
        func_def = {"name" : name, "stmts" : stmts}
        if params: func_def["params"] = params
        if var_defs: func_def["var_defs"] = var_defs
        if type: func_def["type"] = type
        return func_def

    def matches_num(self):
        return self.not_done() and self.token().matches(Token.NUM)

    def get_num(self):
        assert self.matches_num()
        return self.match(Token.NUM).value

    def matches_bool(self):
        return self.not_done() and self.token().matches(Token.BOOL)

    def get_bool(self):
        assert self.matches_bool()
        return self.match(Token.BOOL).value

    def matches_null(self):
        return self.not_done() and self.matches_keyword("None")

    def get_null(self):
        assert self.matches_null()
        self.match(Token.KEYWORD)
        return None

    def matches_literal(self):
        return self.matches_num() or self.matches_bool() or self.matches_null()

    def get_literal(self):
        assert self.matches_literal()
        if self.matches_num():
            return {"value" : self.get_num(), "type" : "int"}
        elif self.matches_bool():
            return {"value" : self.get_bool(), "type" : "bool"}
        elif self.matches_null():
            return {"value" : self.get_null()}
        else:
            self.error()

    def get_stmt(self):
        stmt = None
        if self.matches_pass_stmt():
            stmt = self.get_pass_stmt()
        elif self.matches_print_stmt():
            stmt = self.get_print_stmt()
        elif self.matches_return_stmt():
            stmt = self.get_return_stmt()
        elif self.matches_assign_stmt():
            stmt = self.get_assign_stmt()
        else:
            stmt = self.get_expr()
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

    def matches_pass_stmt(self):
        return self.matches_keyword("pass")

    def get_pass_stmt(self):
        assert self.matches_pass_stmt()
        self.match(Token.KEYWORD)
        return {"stmt" : "pass"}

    def matches_print_stmt(self):
        return self.matches_keyword("print")

    def get_print_stmt(self):
        assert self.matches_print_stmt()
        self.match(Token.KEYWORD)
        self.match(Token.LPAREN)
        expr = self.get_expr()
        self.match(Token.RPAREN)
        return {"stmt" : "print", "expr" : expr}

    def matches_return_stmt(self):
        return self.matches_keyword("return")

    def get_return_stmt(self):
        assert self.matches_return_stmt()
        self.match(Token.KEYWORD)
        stmt = {"stmt" : "return"}
        if not self.matches_newline(): stmt["expr"] = self.get_expr()
        return stmt

    def matches_assign_stmt(self):
        return self.not_done() and self.token().matches(Token.ID) and self.token(1).matches(Token.ASSIGN)

    def get_assign_stmt(self):
        assert self.matches_assign_stmt()
        dest = self.get_identifier()
        self.match(Token.ASSIGN)
        expr = self.get_expr()
        return {"stmt" : "assign", "dest" : dest, "expr" : expr}

    def matches_call_expr(self):
        return self.not_done() and self.token().matches(Token.ID) and self.token(1).matches(Token.LPAREN)

    def get_call_expr(self):
        assert self.matches_call_expr()
        name = self.get_identifier()
        args = []
        self.match(Token.LPAREN)
        if not self.token().matches(Token.RPAREN):
            args.append(self.get_expr())
            while self.token().matches(Token.COMMA):
                self.match(Token.COMMA)
                args.append(self.get_expr())
        self.match(Token.RPAREN)
        expr = {"call" : name}
        if args: expr["args"] = args
        return expr

    def matches_identifier(self):
        return self.not_done() and self.token().matches(Token.ID)

    def get_identifier(self):
        assert self.matches_identifier()
        return self.match(Token.ID).value

    def matches_type(self):
        return self.not_done() and self.token().matches(Token.TYPE)

    def get_type(self):
        assert self.matches_type()
        return self.match(Token.TYPE).value

    def get_expr(self):
        if self.matches_call_expr():
            return self.get_call_expr()
        elif self.matches_literal():
            return self.get_literal()
        elif self.matches_identifier():
            return self.get_identifier()
        else:
            self.error()

    def get_program(self):
        var_defs, func_defs, = [], []
        while self.matches_var_def() or self.matches_func_def():
            if self.matches_var_def():
                var_defs.append(self.get_var_def())
            else:
                func_defs.append(self.get_func_def())
        stmts = self.get_stmts()
        program = {}
        if var_defs: program["var_defs"] = var_defs
        if func_defs: program["func_defs"] = func_defs
        if stmts: program["stmts"] = stmts
        return program

def get_pretty_json_str(d):
    json = pprint.pformat(d, compact=True)
    json = json.replace("'", '"').replace("False", "false").replace("True", "true").replace("None", "null")
    return json

if __name__ == "__main__":
    tokens = list(lex_text(sys.stdin.read()))
    parser = Parser(tokens)
    program = parser.get_program()
    sys.stdout.write(get_pretty_json_str(program))
    sys.stdout.flush()

#  tokens = list(lex_text(open("prog.py").read()))
#  parser = Parser(tokens)
