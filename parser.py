import sys
import json
import myast
from lexer import *

class Parser(object):

    def __init__(self, tokens):
        self.tokens = tokens
        self.size = len(tokens)
        self.pos = 0

    def error(self, msg=""):
        if msg: msg = f": {msg}"
        raise Exception(f"Syntax error{msg}")

    def token(self, peek_amt=0) -> Token | None:
        """
        Returns the token that `peek_amt` away from the current
        one, or None if it doesn't exist. `peek_amt` defaults
        to 0, so the default token is the current one.
        """
        if self.pos + peek_amt < self.size:
            return self.tokens[self.pos + peek_amt]
        else:
            return None

    def advance(self):
        """
        Advance to the next token if it exists.
        """
        if self.pos < self.size:
            self.pos += 1

    def not_done(self) -> bool:
        """
        Returns true if there are still tokens left to match.
        """
        return self.token() is not None

    def matches_newline(self) -> bool:
        return self.not_done() and self.token().matches("NEWLINE")

    def matches_indent(self) -> bool:
        return self.not_done() and self.token().matches("INDENT")

    def matches_dedent(self) -> bool:
        return self.not_done() and self.token().matches("DEDENT")

    def matches_keyword(self, word) -> bool:
        """
        Returns true if current token type is KEYWORD, AND the keyword value itself matches `word`.
        """
        return self.not_done() and self.token().matches(Token.KEYWORD) and self.token().value == word

    def matches_typed_var(self) -> bool:
        """
        Returns true if current tokens match: 'typed_var ::= ID : type'
        """
        return self.not_done() and self.token().matches(Token.ID) and self.token(1).matches(Token.COLON)

    def matches_func_def(self) -> bool:
        """
        Returns true if current tokens match prefix of: 'func_def ::= def ID ({typed_var {, typed_var}*}?) { -> type}? NEWLINE INDENT func_body DEDENT'
        """
        return self.not_done() and self.matches_keyword("def") and self.token(1).matches(Token.ID)

    def matches_num(self) -> bool:
        """
        Returns true if current token is NUM.
        """
        return self.not_done() and self.token().matches(Token.NUM)

    def matches_bool(self) -> bool:
        """
        Returns true if current token is BOOL.
        """
        return self.not_done() and self.token().matches(Token.BOOL)

    def matches_literal(self) -> bool:
        """
        Returns true if current token is a literal: a NUM or a BOOL.
        """
        return self.matches_num() or self.matches_bool()

    def matches_id(self) -> bool:
        """
        Returns true if current token is ID
        """
        return self.not_done() and self.token().matches(Token.ID)

    def matches_type(self) -> bool:
        """
        Returns true if current token is TYPE
        """
        return self.not_done() and self.token().matches(Token.TYPE)

    def matches_pass_stmt(self) -> bool:
        return self.matches_keyword("pass")

    def matches_print_stmt(self) -> bool:
        return self.matches_keyword("print")

    def matches_return_stmt(self) -> bool:
        return self.matches_keyword("return")

    def matches_while_stmt(self) -> bool:
        return self.matches_keyword("while")

    def matches_if_stmt(self) -> bool:
        return self.matches_keyword("if")

    def matches_for_stmt(self) -> bool:
        return self.matches_keyword("for")

    def matches_assign_stmt(self) -> bool:
        return self.matches_id() and self.token(1).matches(Token.ASSIGN)

    def matches_call_expr(self):
        return self.matches_id() and self.token(1).matches(Token.LPAREN)

    def match(self, token) -> Token:
        """
        If the current token has the same "name" (e.g. "LPAREN", "COMMA", "TYPE", etc.)
        as `token`, then we advance to the next token. Otherwise an error is raised.
        """
        matchee = self.token()
        if matchee.matches(token): self.advance()
        else: self.error(f"{token} does not match current token {matchee}")
        return matchee

    def match_newline(self):
        self.match("NEWLINE")

    def match_indent(self):
        self.match("INDENT")

    def match_dedent(self):
        self.match("DEDENT")

    def match_keyword(self, word):
        assert self.matches_keyword(word)
        self.match(Token.KEYWORD)

    def get_pass_stmt(self) -> myast.PassStmt:
        assert self.matches_pass_stmt()
        self.match_keyword("pass")
        return myast.PassStmt()

    def get_print_stmt(self) -> myast.PrintStmt:
        assert self.matches_print_stmt()
        self.match_keyword("print")
        self.match(Token.LPAREN)
        expr = self.get_expr()
        self.match(Token.RPAREN)
        return myast.PrintStmt(expr)

    def get_return_stmt(self) -> myast.ReturnStmt:
        assert self.matches_return_stmt()
        self.match_keyword("return")
        expr = self.get_expr()
        return myast.ReturnStmt(expr)

    def get_assign_stmt(self) -> myast.AssignStmt:
        assert self.matches_assign_stmt()
        dest = self.get_id()
        self.match(Token.ASSIGN)
        expr = self.get_expr()
        return myast.AssignStmt(dest, expr)

    def get_expr_stmt(self) -> myast.ExprStmt:
        expr = self.get_expr()
        return myast.ExprStmt(expr)

    def get_call_expr(self) -> myast.CallExpr:
        assert self.matches_call_expr()
        name = self.get_id()
        args = []
        self.match(Token.LPAREN)
        if not self.token().matches(Token.RPAREN):
            args.append(self.get_expr())
            while self.token().matches(Token.COMMA):
                self.match(Token.COMMA)
                args.append(self.get_expr())
        self.match(Token.RPAREN)
        return myast.CallExpr(name, args)

    def get_atom(self, min_prec=1) -> myast.Expr:
        if self.matches_call_expr():
            return self.get_call_expr()
        elif self.token().matches(Token.LPAREN):
            self.match(Token.LPAREN)
            expr = self.get_expr()
            self.match(Token.RPAREN)
            return expr
        elif self.token().matches(Token.NOT) or self.token().matches(Token.SUB):
            op = self.token().name
            self.advance()
            expr = self.get_expr()
            return myast.UnOpExpr(op, expr)
        elif self.matches_literal():
            return self.get_literal()
        elif self.matches_id():
            return self.get_id_expr()
        else:
            self.error()

    def get_expr(self, min_prec=1) -> myast.Expr:
        lhs = self.get_atom()
        while self.not_done() and Token.get_precedence(self.token().name) >= min_prec:
            op = self.token().name
            prec = Token.get_precedence(op)
            self.advance()
            lhs = myast.BinOpExpr(op, lhs, self.get_expr(prec+1))
        return lhs

    def get_id(self) -> str:
        """
        Parses an identifier into a string.
        """
        assert self.matches_id()
        return self.match(Token.ID).value

    def get_type(self) -> str:
        """
        Parses a type into one of the following strings: "int" or "bool"
        """
        assert self.matches_type()
        return self.match(Token.TYPE).value

    def get_num(self) -> int:
        assert self.matches_num()
        return self.match(Token.NUM).value

    def get_bool(self) -> str:
        assert self.matches_bool()
        return self.match(Token.BOOL).value

    def get_literal(self) -> myast.Literal:
        """
        Parses a literal into a myast.Literal object.
        """
        assert self.matches_literal()

        if self.matches_num():
            return myast.Literal(self.get_num(), "int")
        elif self.matches_bool():
            return myast.Literal(self.get_bool(), "bool")
        else:
            self.error()

    def get_id_expr(self) -> myast.IdExpr:
        assert self.matches_id()
        return myast.IdExpr(self.get_id())

    def get_typed_var(self) -> myast.TypedVar:
        """
        Parses a typed variable into a myast.TypedVar object.
        """
        assert self.matches_typed_var()
        name = self.get_id()
        self.match(Token.COLON)
        type = self.get_type()
        return myast.TypedVar(name, type)

    def get_var_def(self) -> myast.VarDef:
        """
        Parses a variable definition into a myast.VarDef object.
        """
        assert self.matches_typed_var()
        typed_var = self.get_typed_var()
        self.match(Token.ASSIGN)
        literal = self.get_literal()
        self.match_newline()
        return myast.VarDef(typed_var, literal)

    def get_block(self) -> list[myast.Stmt]:
        self.match_newline()
        self.match_indent()
        block = [self.get_stmt()]
        while not self.matches_dedent():
            block.append(self.get_stmt())
        self.match_dedent()
        return block

    def get_for_stmt(self) -> myast.ForStmt:
        self.match_keyword("for")
        iter_name = self.get_id()
        self.match_keyword("in")
        self.match_keyword("range")
        self.match(Token.LPAREN)
        bounds = [self.get_num()]
        if self.token().matches(Token.COMMA):
            self.match(Token.COMMA)
            bounds.append(self.get_num())
        self.match(Token.RPAREN)
        self.match(Token.COLON)
        block = self.get_block()
        return myast.ForStmt(iter_name, bounds, block)

    def get_while_stmt(self) -> myast.WhileStmt:
        self.match_keyword("while")
        cond = self.get_expr()
        self.match(Token.COLON)
        block = self.get_block()
        return myast.WhileStmt(cond, block)

    def get_if_stmt(self) -> myast.IfStmt:
        self.match_keyword("if")
        cond = self.get_expr()
        self.match(Token.COLON)
        if_block = self.get_block()
        elif_blocks = []
        else_block = None
        while self.matches_keyword("elif"):
            self.match_keyword("elif")
            lcond = self.get_expr()
            self.match(Token.COLON)
            lblock = self.get_block()
            elif_blocks.append((lcond, lblock))
        if self.matches_keyword("else"):
            self.match_keyword("else")
            self.match(Token.COLON)
            else_block = self.get_block()
        return myast.IfStmt(cond, if_block, elif_blocks, else_block)

    def get_stmt(self) -> myast.Stmt:
        if self.matches_while_stmt():
            return self.get_while_stmt()
        elif self.matches_for_stmt():
            return self.get_for_stmt()
        elif self.matches_if_stmt():
            return self.get_if_stmt()
        else:
            stmt = self.get_simple_stmt()
            self.match_newline()
            return stmt

    def get_simple_stmt(self) -> myast.Stmt:
        if self.matches_while_stmt():
            return self.get_while_stmt()
        if self.matches_pass_stmt():
            return self.get_pass_stmt()
        elif self.matches_print_stmt():
            return self.get_print_stmt()
        elif self.matches_return_stmt():
            return self.get_return_stmt()
        elif self.matches_assign_stmt():
            return self.get_assign_stmt()
        else:
            return self.get_expr_stmt()

    def get_func_body(self) -> myast.FuncBody:
        """
        Parses a function body into a myast.FuncBody object.
        """

        var_defs: list[myast.VarDef] = [] # function variable definitions (those defined in the body of function, NOT parameters)
        stmts: list[myast.Stmt] = [] # function body statements

        """
        Parse function variable definitions
        """
        while self.matches_typed_var(): var_defs.append(self.get_var_def())

        """
        Parse function body statements
        """
        while not self.matches_dedent(): stmts.append(self.get_stmt())

        return myast.FuncBody(var_defs, stmts)

    def get_func_def(self) -> myast.FuncDef:
        """
        Parses a function definition into a myast.FuncDef object.
        """
        assert self.matches_func_def() # func_def ::= def ID ({typed_var {, typed_var}*}?) { -> type}? NEWLINE INDENT func_body DEDENT

        name: str = None # function identifier
        params: list[myast.TypedVar] = [] # function parameters
        type: str = None # function return type
        body: myast.FuncBody = None # function body

        """
        Parse function identifier (required)
        """
        self.match_keyword("def")
        name = self.get_id()
        self.match(Token.LPAREN)

        """
        Parse function parameters (defaults to no parameters)
        """
        if self.matches_typed_var():
            params.append(self.get_typed_var())
            while self.token().matches(Token.COMMA):
                self.match(Token.COMMA)
                params.append(self.get_typed_var())
        self.match(Token.RPAREN)

        """
        Parse function return type (defaults to no return type)
        """
        if self.token().matches(Token.ARROW):
            self.match(Token.ARROW)
            type = self.get_type()

        """
        Parse function body (required)
        """
        self.match(Token.COLON)
        self.match_newline()
        self.match_indent()
        body = self.get_func_body()
        self.match_dedent()

        return myast.FuncDef(name, params, type, body)

    def get_func_defs(self) -> list[myast.FuncDef]:
        """
        Parses all top-level function definitions into a list of myast.FuncDef objects.
        """
        func_defs = []
        while self.matches_func_def(): func_defs.append(self.get_func_def())
        return func_defs

    def get_program(self) -> myast.Program:
        """
        Parses a valid ChocoPy program (in reality, just a subset) into a myast.Program object.
        """
        func_defs = self.get_func_defs()
        return myast.Program(func_defs)

if __name__ == "__main__":
    tokens = list(lex_text(sys.stdin.read()))
    parser = Parser(tokens)
    program = parser.get_program()
    json.dump(program.get_bril(), sys.stdout, indent=4)
