from lexer import Token
from code import Body, Program, Function
from myast import *

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

    def matches_typed_var(self):
        return self.not_done() and self.token().matches(Token.ID) and self.token(1).matches(Token.COLON)

    def get_typed_var(self):
        name = self.match(Token.ID).value
        self.match(Token.COLON)
        type = self.match(Token.TYPE).value
        return name, type

    def get_var_def(self):
        name, type = self.get_typed_var()
        self.match(Token.ASSIGN)
        if type == "int": value = self.match(Token.NUM).value
        elif type == "bool": value = self.match(Token.BOOL).value
        else: self.error(f"unknown type: {type}")
        self.match_newline()
        return name, value, type

    def matches_func_def(self):
        return self.not_done() and self.matches_keyword("def") and self.token(1).matches(Token.ID)

    def get_func_sig(self):
        sig = [self.get_typed_var()]
        while self.token().matches(Token.COMMA):
            self.match(Token.COMMA)
            sig.append(self.get_typed_var())
        return sig

    def get_func_def(self):
        self.match(Token.KEYWORD)
        name = self.match(Token.ID).value
        self.match(Token.LPAREN)
        sig = []
        if self.matches_typed_var(): sig = self.get_func_sig()
        self.match(Token.RPAREN)
        ret_type = None
        if self.token().matches(Token.ARROW):
            self.match(Token.ARROW)
            ret_type = self.match(Token.TYPE).value
        self.match(Token.COLON)
        self.match_newline()
        self.match_indent()
        table, stmts = self.get_func_body()
        self.match_dedent()
        return Function(table, stmts, name, sig, ret_type)

    def get_func_body(self):
        func_table = self.get_table()
        func_stmts = []
        while not self.token().matches("DEDENT"):
            func_stmts.append(self.get_stmt())
        return func_table, func_stmts

    def get_table(self):
        table = {}
        while self.matches_typed_var():
            name, value, type = self.get_var_def()
            table[name] = {"value" : value, "type" : type}
        return table

    def parse(self):
        table, funcs = {}, {}
        while self.token():
            if self.matches_func_def():
                func = self.get_func_def()
                funcs[func.name] = func
            elif self.matches_typed_var():
                name, value, type = self.get_var_def()
                table[name] = {"value" : value, "type" : type}
            else:
                break
        stmts = self.get_stmts()
        return Program(table, stmts, funcs)

    def matches_keyword(self, word):
        return self.not_done() and self.token().matches(Token.KEYWORD) and self.token().value == word

    def get_print(self):
        self.match(Token.KEYWORD)
        self.match(Token.LPAREN)
        stmt = AstPrint(expr=self.get_expr())
        self.match(Token.RPAREN)
        return stmt

    def get_return(self):
        self.match(Token.KEYWORD)
        return AstReturn(expr=self.get_expr())

    def matches_assign(self):
        return self.not_done() and self.token().matches(Token.ID) and self.token(1).matches(Token.ASSIGN)

    def get_assign(self):
        target = AstVariable(name=self.match(Token.ID).value)
        self.match(Token.ASSIGN)
        stmt = AstAssign(target=target, expr=self.get_expr())
        return stmt

    def get_stmts(self):
        stmts = []
        while self.token(): stmts.append(self.get_stmt())
        return stmts

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

    def matches_func_call(self):
        return self.not_done() and self.token().matches(Token.ID) and self.token(1).matches(Token.LPAREN)

    def get_func_call(self):
        name = self.match(Token.ID).value
        self.match(Token.LPAREN)
        params = []
        if not self.token().matches(Token.RPAREN):
            params.append(self.get_expr())
            while self.token().matches(Token.COMMA):
                self.match(Token.COMMA)
                params.append(self.get_expr())
        self.match(Token.RPAREN)
        return AstCall(name, params)

    def get_atom(self):
        if self.matches_func_call():
            return self.get_func_call()
        elif self.token().matches(Token.LPAREN):
            self.match(Token.LPAREN)
            expr = self.get_expr()
            self.match(Token.RPAREN)
            return expr
        elif self.token().matches(Token.SUB):
            self.advance()
            if self.token().matches(Token.NUM):
                return AstLiteral(value=self.match(Token.NUM).value * -1, type="int")
            else:
                return AstUnOp(op="USUB", expr=self.get_expr())
        elif self.token().matches(Token.NOT):
            self.advance()
            return AstUnOp(op="NOT", expr=self.get_expr())
        elif self.token().matches(Token.NUM):
            return AstLiteral(value=self.match(Token.NUM).value, type="int")
        elif self.token().matches(Token.BOOL):
            return AstLiteral(value=self.match(Token.BOOL).value, type="bool")
        elif self.token().matches(Token.ID):
            return AstVariable(self.match(Token.ID).value)
        else:
            self.error()

    def get_expr(self, min_prec=1):
        lhs = self.get_atom()
        while self.token() and Token.get_precedence(self.token().name) >= min_prec:
            op = self.token().name
            prec = Token.get_precedence(op)
            self.advance()
            lhs = AstBinOp(op=op, left=lhs, right=self.get_expr(prec+1))
        return lhs
