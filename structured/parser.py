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

    def matches_assign_stmt(self):
        return self.not_done() and self.token().matches(Token.ID) and self.token(1).matches(Token.ASSIGN)

    def matches_call_expr(self):
        return self.not_done() and self.token().matches(Token.ID) and self.token(1).matches(Token.LPAREN)

    def matches_literal(self):
        return self.not_done() and (self.token().matches(Token.NUM) or self.token().matches(Token.BOOL) or self.matches_keyword("None"))

    def matches_identifier(self):
        return self.not_done() and self.token().matches(Token.ID)

    def not_done(self):
        return self.token() is not None

    def get_typed_var(self):
        """
        @grammar :: typed_var ::= ID : type
        @dict    :: {"id" : ID, "type" : type}
        """
        assert self.matches_typed_var()
        name = self.match(Token.ID).value
        self.match(Token.COLON)
        type = self.match(Token.TYPE).value
        return {"id" : name, "type" : type}

    def get_identifier(self):
        assert self.matches_identifier()
        name = self.match(Token.ID).value
        return {"id" : name}

    def get_call_expr(self):
        """
        @grammar :: call_expr ::= ID ({expr {, expr}*}?)
        @dict    :: {"call" : ID, "args" : [expr, ...]}
        """
        assert self.matches_call_expr()
        name = self.match(Token.ID).value
        args = []
        self.match(Token.LPAREN)
        if not self.token().matches(Token.RPAREN):
            args.append(self.get_expr())
            while self.token().matches(Token.COMMA):
                self.match(Token.COMMA)
                args.append(self.get_expr())
        self.match(Token.RPAREN)
        return {"call" : name, "args" : args}

    def get_expr(self):
        """
        @grammar :: expr ::= call_expr | literal | ID
        @dict ...
        """
        if self.matches_call_expr():
            return self.get_call_expr()
        elif self.matches_literal():
            return self.get_literal()
        elif self.matches_identifier():
            return self.get_identifier()
        else:
            self.error()

    def get_literal(self):
        """
        @grammar :: literal ::= NUM | ID | None
        @dict    :: {"literal" : literal, {"type" : type}?}
        """
        assert self.matches_literal()
        if self.matches_keyword("None"):
            self.match(Token.KEYWORD)
            return {"literal" : None}
        elif self.token().matches(Token.NUM):
            value = self.match(Token.NUM).value
            return {"literal" : value, "type" : "int"}
        elif self.token().matches(Token.BOOL):
            value = self.match(Token.BOOL).value
            return {"literal" : value, "type" : "bool"}
        else:
            self.error()

    def get_var_def(self):
        """
        @grammar :: var_def ::= typed_var = literal NEWLINE
        @dict    :: {"typed_var" : typed_var, "literal" : literal}
        """
        assert self.matches_typed_var()
        typed_var = self.get_typed_var()
        self.match(Token.ASSIGN)
        literal = self.get_literal()
        if "type" in literal: assert typed_var["type"] == literal["type"]
        self.match_newline()
        return {"typed_var" : typed_var, "literal" : literal["literal"]}

    def get_decls(self):
        """
        @grammar :: decls ::= {var_def | func_def}*
        @dict    :: {"var_defs" : [var_def..], "func_def" : [func_def..]}
        """
        var_defs, func_defs = [], []
        while True:
            if self.matches_typed_var(): var_defs.append(self.get_var_def())
            elif self.matches_func_def(): func_defs.append(self.get_func_def())
            else: break
        return {"var_defs" : var_defs, "func_defs" : func_defs}

    def get_func_body(self):
        """
        @grammar :: var_def* stmt+
        @dict    :: {"var_defs" : [var_def..], "stmts" : [stmt..]}
        """
        func_body = self.get_decls()
        assert len(func_body["func_defs"]) == 0
        del func_body["func_defs"]
        func_body["stmts"] = self.get_func_stmts()
        return func_body

    def get_func_def(self):
        """
        @grammar :: func_def ::= "def" ID ( {typed_var{, typed_var}*}?) {-> type}? : NEWLINE INDENT func_body DEDENT
        @dict    :: {"name" : ID, "params" : [typed_var..], "type" : type, "func_body" : func_body}
        """
        assert self.matches_keyword("def")
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
            type = self.match(Token.TYPE).value
        self.match(Token.COLON)
        self.match_newline()
        self.match_indent()
        func_body = self.get_func_body()
        self.match_dedent()
        return {"name" : name, "params" : params, "type" : type, "func_body" : func_body}

    def get_pass_stmt(self):
        """
        @grammar :: pass_stmt ::= "pass"
        @dict    :: {"stmt" : "pass"}
        """
        assert self.matches_keyword("pass")
        self.match(Token.KEYWORD)
        return {"stmt" : "pass"}

    def get_print_stmt(self):
        """
        @grammar :: print_stmt ::= "print" (expr)
        @dict    :: {"stmt" : "print", "expr" : expr}
        """
        assert self.matches_keyword("print")
        self.match(Token.KEYWORD)
        self.match(Token.LPAREN)
        expr = self.get_expr()
        self.match(Token.RPAREN)
        return {"stmt" : "print", "expr" : expr}

    def get_return_stmt(self):
        """
        @grammar :: return_stmt ::= "return" {expr}?
        @dict    :: {"stmt" : "return", "expr" : expr}
        """
        assert self.matches_keyword("return")
        self.match(Token.KEYWORD)
        stmt = {"stmt" : "return"}
        if not self.matches_newline(): stmt["expr"] = self.get_expr()
        return stmt

    def get_assign_stmt(self):
        """
        @grammar :: assign_stmt ::= ID = expr
        @dict    :: {"stmt" : "assign", "dest" : ID, "expr" : expr}
        """
        assert self.matches_assign_stmt()
        dest = self.match(Token.ID).value
        self.match(Token.ASSIGN)
        expr = self.get_expr()
        return {"stmt" : "assign", "dest" : dest, "expr" : expr}

    def get_stmt(self):
        """
        @grammar :: stmt ::= {pass_stmt | print_stmt | return_stmt | assign_stmt | expr} NEWLINE
        @dict ...
        """
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
#  decls = program["decls"]
#  stmts = program["stmts"]

#  var_defs = decls["var_defs"]
#  func_defs = decls["func_defs"]

if __name__ == "__main__":
    tokens = list(lex_text(sys.stdin.read()))
    parser = Parser(tokens)
    program = parser.get_program()
    sys.stdout.write(get_pretty_json_str(program))
    sys.stdout.flush()
