import sys
import json
from lex import Token

class Ast(object):
    pass

class AstProgram(Ast):

    def __init__(self, var_defs, stmts):
        self.var_defs = var_defs
        self.stmts = stmts

class AstVarDef(Ast):

    def __init__(self, var_id, var_type, literal):
        self.id = var_id
        self.type = var_type
        self.literal = literal

    def __repr__(self):
        return f"AstVarDef(id={self.id}, type={self.type}, literal={self.literal})"

class AstAssign(Ast):

    def __init__(self, target, expr):
        self.target = target
        self.expr = expr

class AstPrint(Ast):

    def __init__(self, expr):
        self.expr = expr

class AstBinOp(Ast):

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class Parser(object):

    def __init__(self, tokens):
        self.tokens = tokens
        self.size = len(tokens)
        self.pos = 0
        self.token = self.tokens[self.pos]

    def error(self, msg=None):
        raise Exception("Syntax error" if not msg else f"Syntax error: {msg}")

    def peek(self):
        if self.pos + 1 < self.size:
            return self.tokens[self.pos + 1]
        else:
            return None

    def next(self):
        self.token = self.peek()
        if self.token:
            self.pos += 1
            return self.token
        else:
            return None

    def match(self, token):
        matchee = self.token
        if self.token == token: self.next()
        else: self.error()
        return matchee

    def parse(self):
        return self.program()

    def program(self):
        var_defs = self.var_defs()
        stmts = self.stmts()
        stmts = []
        return AstProgram(var_defs, stmts)

    def var_defs(self):
        l = []
        while self.peek() == Token("DELIM", ":"):
            l.append(self.var_def())
        return l

    def var_def(self):
        id_token = self.match(Token("ID"))
        self.match(Token("DELIM", ":"))
        type_token = self.match(Token("TYPE"))
        self.match(Token("DELIM", "="))
        if type_token.value == "int":
            lit_token = self.match(Token("NUM"))
        elif type_token.value == "bool":
            lit_token = self.match(Token("BOOL"))
        else:
            self.error("variable definition literal types don't match")
        self.match(Token("NEWLINE"))
        return AstVarDef(id_token.value, type_token.value, lit_token.value)

    def stmts(self):
        l = []
        while self.token: l.append(self.stmt())
        return l

    def stmt(self):
        node = None
        if self.token == Token("PRINT"):
            self.match(Token("PRINT"))
            self.match(Token("DELIM", "("))
            node = AstPrint(self.expr())
            self.match(Token("DELIM", ")"))
        elif self.token == Token("ID") and self.peek() == Token("DELIM", "="):
            target_token = self.match(Token("ID"))
            self.match(Token("DELIM", "="))
            expr = self.expr()
            node = AstAssign(target_token.value, expr)
        else:
            node = self.expr()

        self.match(Token("NEWLINE"))
        return node

    def expr(self):
        node = self.term()
        while self.token and self.token.value in {"+", "-"}:
            op = self.token.value
            self.match(Token("BINOP", op))
            node = AstBinOp(op=op, left=node, right=self.term())
        return node

    def term(self):
        node = self.factor()
        while self.token and self.token.value in {"+", "//", "%"}:
            op = self.token.value
            self.match(Token("BINOP", op))
            node = AstBinOp(op=op, left=node, right=self.factor())
        return node

    def factor(self):
        if self.token == Token("DELIM", "("):
            self.match(Token("DELIM", "("))
            node = self.expr()
            self.match(Token("DELIM", ")"))
            return node
        elif self.token == Token("NUM"):
            node = self.token.value
            self.match(Token("NUM"))
            return node
        elif self.token == Token("ID"):
            node = self.token.value
            self.match(Token("ID"))
            return node
        else:
            self.error()

if __name__ == "__main__":
    #  tokens = [Token.from_dict(token) for token in json.load(sys.stdin)]
    tokens = [Token.from_dict(token) for token in json.load(open("test1.json"))]
    parser = Parser(tokens)
    program = parser.parse()

