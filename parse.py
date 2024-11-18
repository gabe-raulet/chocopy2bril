import sys
import json
from lex import Lexer, Token

class Ast(object):
    pass

class AstBody(Ast):

    def __init__(self, first_stmt):
        self.stmts = [first_stmt]

    def append_stmt(self, stmt):
        self.stmts.append(stmt)

    def to_dict(self):
        body_dict = {}
        body_dict["ast"] = "body"
        body_dict["stmts"] = [stmt.to_dict() for stmt in self.stmts]
        return body_dict

    def __repr__(self):
        return f"AstBody(stmts={self.stmts})"

class AstAssign(Ast):

    def __init__(self, target, expression):
        self.target = target
        self.expression = expression

    def to_dict(self):
        assign_dict = {}
        assign_dict["ast"] = "assign"
        assign_dict["target"] = self.target.to_dict()
        assign_dict["expr"] = self.expression.to_dict()
        return assign_dict

    def __repr__(self):
        return f"AstAssign(target={self.target}, expr={self.expression})"

class AstPrint(Ast):

    def __init__(self, expression):
        self.expression = expression

    def to_dict(self):
        print_dict = {}
        print_dict["ast"] = "print"
        print_dict["expr"] = self.expression.to_dict()
        return print_dict

    def __repr__(self):
        return f"AstPrint(expr={self.expression})"

class AstTerm(Ast):

    def __init__(self, token):
        self.token = token

    def to_dict(self):
        term_dict = {}
        term_dict["ast"] = "term"
        term_dict["name"] = self.token.name
        term_dict["value"] = self.token.value
        return term_dict

    def __repr__(self):
        return f"AstTerm({self.token})"

class AstBinOp(Ast):

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def to_dict(self):
        binop_dict = {}
        binop_dict["ast"] = "binop"
        binop_dict["op"] = self.op
        binop_dict["left"] = self.left.to_dict()
        binop_dict["right"] = self.right.to_dict()


    def __repr__(self):
        return f"AstBinOp(op={self.op}, left={self.left}, right={self.right})"

class Parser(object):

    def __init__(self, tokens):
        self.tokens = tokens
        self.size = len(self.tokens)
        self.pos = 0
        self.token = self.tokens[self.pos]

    def error(self):
        raise Exception("Syntax error")

    def advance(self):
        if self.pos + 1 < self.size:
            self.pos += 1
            self.token = self.tokens[self.pos]
        else:
            self.token = None

    def peek(self):
        if self.pos + 1 < self.size:
            return self.tokens[self.pos + 1]
        else:
            return None

    def match(self, token_name):
        if self.token.name == token_name:
            self.advance()
        else:
            self.error()

    def parse(self):
        return self.stmts()

    def stmts(self):
        body = AstBody(self.stmt())
        while self.token: body.append_stmt(self.stmt())
        return body

    def stmt(self):
        node = None
        if self.token.name == Token.PRINT:
            self.match(Token.PRINT)
            node = AstPrint(expression=self.expr())
        elif self.token.name == Token.ID and self.peek().name == Token.ASSIGN:
            target = self.token
            self.match(Token.ID)
            self.match(Token.ASSIGN)
            node = AstAssign(target=target, expression=self.expr())
        else:
            node = self.expr()

        if self.token.name == Token.NEWLINE:
            self.match(Token.NEWLINE)

        return node

    def expr(self):
        node = self.term()
        while self.token and self.token.name in {Token.PLUS, Token.MINUS}:
            op = self.token.name
            self.match(op)
            node = AstBinOp(op=op, left=node, right=self.term())
        return node

    def term(self):
        node = self.factor()
        while self.token and self.token.name in {Token.MUL, Token.DIV}:
            op = self.token.name
            self.match(op)
            node = AstBinOp(op=op, left=node, right=self.factor())
        return node

    def factor(self):
        if self.token.name == Token.LPAREN:
            self.match(Token.LPAREN)
            node = self.expr()
            self.match(Token.RPAREN)
            return node
        elif self.token.name == Token.NUM:
            node = AstTerm(self.token)
            self.match(Token.NUM)
            return node
        elif self.token.name == Token.ID:
            node = AstTerm(self.token)
            self.match(Token.ID)
            return node
        else:
            self.error()

if __name__ == "__main__":
    tokens = Lexer.read_dict_tokens(json.load(sys.stdin))
    parse_tree = Parser(tokens).parse()
    parse_tree_json = parse_tree.to_dict()
    json.dump(parse_tree_json, sys.stdout, indent=4)
