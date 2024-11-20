import sys
import json
from lex import Token, Lexer

class Ast(object):
    pass

class AstBody(Ast):

    def __init__(self, first_stmt):
        self.stmts = [first_stmt]

    def append_stmt(self, stmt):
        self.stmts.append(stmt)

    def __iter__(self):
        for stmt in self.stmts:
            yield stmt

    def to_dict(self):
        return {"ast" : "body", "stmts" : [stmt.to_dict() for stmt in self]}

class AstAssign(Ast):

    def __init__(self, target, expr):
        self.target = target
        self.expr = expr

    def to_dict(self):
        return {"ast" : "assign", "target" : self.target, "expr" : self.expr.to_dict()}

class AstPrint(Ast):

    def __init__(self, expr):
        self.expr = expr

    def to_dict(self):
        return {"ast" : "print", "expr" : self.expr.to_dict()}

class AstConstant(Ast):

    def __init__(self, value):
        self.value = value

    def to_dict(self):
        return {"ast" : "constant", "value" : self.value}

class AstName(Ast):

    def __init__(self, name):
        self.name = name

    def to_dict(self):
        return {"ast" : "name", "name" : self.name}

class AstBinaryOp(Ast):

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def to_dict(self):
        return {"ast" : "binaryop", "op" : self.op, "left" : self.left.to_dict(), "right" : self.right.to_dict()}

class Parser(object):

    def __init__(self, tokens):
        self.tokens = tokens
        self.size = len(tokens)
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
            self.match(Token.LPAREN)
            node = AstPrint(expr=self.expr())
            self.match(Token.RPAREN)
        elif self.token.name == Token.ID and self.peek().name == Token.ASSIGN:
            target = self.token
            self.match(Token.ID)
            self.match(Token.ASSIGN)
            node = AstAssign(target=target.value, expr=self.expr())
        else:
            node = self.expr()

        if self.token.name == Token.NEWLINE:
            self.match(Token.NEWLINE)

        return node

    def expr(self):
        node = self.term()
        while self.token and self.token.name in {Token.ADD, Token.SUB}:
            op = self.token.name
            self.match(op)
            node = AstBinaryOp(op=op, left=node, right=self.term())
        return node

    def term(self):
        node = self.factor()
        while self.token and self.token.name in {Token.MUL, Token.DIV}:
            op = self.token.name
            self.match(op)
            node = AstBinaryOp(op=op, left=node, right=self.factor())
        return node

    def factor(self):
        if self.token.name == Token.LPAREN:
            self.match(Token.LPAREN)
            node = self.expr()
            self.match(Token.RPAREN)
            return node
        elif self.token.name == Token.NUM:
            node = AstConstant(value=self.token.value)
            self.match(Token.NUM)
            return node
        elif self.token.name == Token.ID:
            node = AstName(name=self.token.value)
            self.match(Token.ID)
            return node
        else:
            self.error()

    @classmethod
    def from_lexer(cls, lexer):
        lexer.reset()
        return cls(list(lexer))

if __name__ == "__main__":
    token_dicts = json.load(sys.stdin)
    tokens = [Token.from_dict(token) for token in token_dicts]
    parser = Parser(tokens)
    body = parser.parse().to_dict()
    json.dump(body, sys.stdout, indent=4)
