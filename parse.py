import sys
import json
from lex import Token, Lexer

class AST_Node(object):
    pass

class AST_BinaryOp(AST_Node):

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinaryOp({self.op}, {self.left}, {self.right})"

class AST_Terminal(AST_Node):

    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return f"Terminal({self.token})"

class Parser(object):

    def __init__(self, lexer):
        self.lexer = lexer
        self.token = self.lexer.next_token()

    def error(self):
        raise Exception("Syntax error")

    def match(self, token_name):
        if self.token.name == token_name:
            self.token = self.lexer.next_token()
        else:
            self.error()

    def parse(self):
        return self.expr()

    def expr(self):
        node = self.term()
        while self.token and self.token.name in {Token.PLUS, Token.MINUS}:
            op = self.token.name
            self.match(op)
            node = AST_BinaryOp(op=op, left=node, right=self.term())
        return node

    def term(self):
        node = self.factor()
        while self.token and self.token.name in {Token.MUL, Token.DIV}:
            op = self.token.name
            self.match(op)
            node = AST_BinaryOp(op=op, left=node, right=self.factor())
        return node

    def factor(self):
        if self.token.name == Token.LPAREN:
            self.match(Token.LPAREN)
            node = self.expr()
            self.match(Token.RPAREN)
            return node
        elif self.token.name == Token.NUM:
            node = AST_Terminal(self.token)
            self.match(Token.NUM)
            return node
        elif self.token.name == Token.ID:
            node = AST_Terminal(self.token)
            self.match(Token.ID)
            return node
        else:
            self.error()

#  program = "".join([line for line in open("p1.txt", "r")])
program = "(123 * 51 + 32) * 12 - 1235"
lexer = Lexer(program)
tree = Parser(lexer).parse()
