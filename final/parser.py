import sys
import json
from lexer import *
import pprint
from myast import *

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

    def match_keyword(self, word):
        assert self.matches_keyword(word)
        self.match(Token.KEYWORD)

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
        return TypedVar(name, type)

    def matches_var_def(self):
        return self.matches_typed_var()

    def get_var_def(self):
        assert self.matches_var_def()
        typed_var = self.get_typed_var()
        self.match(Token.ASSIGN)
        literal = self.get_literal()
        self.match_newline()
        return VarDef(typed_var, literal)

    def matches_func_def(self):
        return self.not_done() and self.matches_keyword("def") and self.token(1).matches(Token.ID)

    def get_func_def(self):
        assert self.matches_func_def()
        self.match_keyword("def")
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
        return FuncDef(name, stmts, var_defs, params, type)

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

    def matches_literal(self):
        return self.matches_num() or self.matches_bool()

    def get_literal(self):
        assert self.matches_literal()
        if self.matches_num():
            return Literal(self.get_num(), "int")
        elif self.matches_bool():
            return Literal(self.get_bool(), "bool")
        else:
            self.error()

    def get_stmt(self):
        if self.matches_if_stmt():
            return self.get_if_stmt()
        else:
            stmt = self.get_simple_stmt()
            self.match_newline()
            return stmt

    def get_simple_stmt(self):
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
            stmt = self.get_expr_stmt()
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
        self.match_keyword("pass")
        return PassStmt()

    def get_block(self):
        self.match_newline()
        self.match_indent()
        stmts = [self.get_stmt()]
        while not self.matches_dedent():
            stmts.append(self.get_stmt())
        self.match_dedent()
        return stmts

    def matches_if_stmt(self):
        return self.matches_keyword("if")

    def get_if_stmt(self):
        self.match_keyword("if")
        if_cond = self.get_expr()
        self.match(Token.COLON)
        if_block = self.get_block()
        else_block = None
        if self.not_done() and self.matches_keyword("else"):
            self.match_keyword("else")
            self.match(Token.COLON)
            else_block = self.get_block()
        return IfStmt(if_cond, if_block, else_block)

    def matches_print_stmt(self):
        return self.matches_keyword("print")

    def get_print_stmt(self):
        assert self.matches_print_stmt()
        self.match_keyword("print")
        self.match(Token.LPAREN)
        expr = self.get_expr()
        self.match(Token.RPAREN)
        return PrintStmt(expr)

    def matches_return_stmt(self):
        return self.matches_keyword("return")

    def get_return_stmt(self):
        assert self.matches_return_stmt()
        self.match_keyword("return")
        expr = self.get_expr()
        return ReturnStmt(expr)

    def matches_assign_stmt(self):
        return self.not_done() and self.token().matches(Token.ID) and self.token(1).matches(Token.ASSIGN)

    def get_assign_stmt(self):
        assert self.matches_assign_stmt()
        dest = self.get_identifier()
        self.match(Token.ASSIGN)
        expr = self.get_expr()
        return AssignStmt(dest, expr)

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
        return CallExpr(name, args)

    def matches_identifier(self):
        return self.not_done() and self.token().matches(Token.ID)

    def get_identifier(self):
        assert self.matches_identifier()
        return self.match(Token.ID).value

    def get_id_expr(self):
        assert self.matches_identifier()
        return IdExpr(self.get_identifier())

    def matches_type(self):
        return self.not_done() and self.token().matches(Token.TYPE)

    def get_type(self):
        assert self.matches_type()
        return self.match(Token.TYPE).value

    def get_expr_stmt(self):
        expr = self.get_expr()
        return ExprStmt(expr)

    def get_atom(self, min_prec=1):
        if self.matches_call_expr():
            return self.get_call_expr()
        elif self.token().matches(Token.LPAREN):
            self.match(Token.LPAREN)
            expr = self.get_expr()
            self.match(Token.RPAREN)
            return expr
        elif self.token().matches(Token.NOT):
            self.advance()
            return UnOpExpr(op="NOT", expr=self.get_expr())
        elif self.matches_literal():
            return self.get_literal()
        elif self.matches_identifier():
            return self.get_id_expr()
        else:
            self.error()

    def get_expr(self, min_prec=1):
        lhs = self.get_atom()
        while self.not_done() and Token.get_precedence(self.token().name) >= min_prec:
            op = self.token().name
            prec = Token.get_precedence(op)
            self.advance()
            lhs = BinOpExpr(op=op, left=lhs, right=self.get_expr(prec+1))
        return lhs

    def get_decls(self):
        var_defs, func_defs = [], []
        while self.matches_var_def() or self.matches_func_def():
            if self.matches_var_def():
                var_defs.append(self.get_var_def())
            else:
                func_defs.append(self.get_func_def())
        return var_defs, func_defs

    def get_program(self):
        var_defs, func_defs = self.get_decls()
        stmts = self.get_stmts()
        return Program(var_defs, func_defs, stmts)

#  if __name__ == "__main__":
    #  tokens = list(lex_text(sys.stdin.read()))
    #  parser = Parser(tokens)
    #  program = parser.get_program()
    #  json.dump(program.get_bril(), sys.stdout, indent=4)

tokens = list(lex_text(open("ifstmt.py").read()))
parser = Parser(tokens)
program = parser.get_program()
json.dump(program.get_bril(), sys.stdout, indent=4)
