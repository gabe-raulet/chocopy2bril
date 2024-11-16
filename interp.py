
class Lexer(object):

    def __init__(self, program):
        self.program = program
        self.size = len(self.program)
        self.pos = 0
        self.cur = self.program[self.pos]

    def advance(self):
        if self.pos + 1 < self.size:
            self.pos += 1
            self.cur = self.program[self.pos]
        else:
            self.cur = None

    def skip_whitespace(self):
        while self.cur and self.cur.isspace():
            self.advance()

    def number(self):
        digits = []
        while self.cur and self.cur.isdigit():
            digits.append(self.cur)
            self.advance()
        return int("".join(digits))

    def identifier(self):
        chars = []
        assert self.cur.isalpha() or self.cur == "_"
        chars.append(self.cur)
        self.advance()
        while self.cur and (self.cur.isalnum() or self.cur == "_"):
            chars.append(self.cur)
            self.advance()
        return "".join(chars)

    def next_token(self):
        self.skip_whitespace()
        token = None
        if self.cur:
            if self.cur.isdigit():
                token = {"num" : self.number()}
            elif self.cur.isalpha() or self.cur == "_":
                token = {"id" : self.identifier()}
            elif self.cur == "(":
                token = {"lparen" : "("}
                self.advance()
            elif self.cur == ")":
                token = {"rparen" : ")"}
                self.advance()
            elif self.cur in {"+", "*"}:
                token = {"op" : self.cur}
                self.advance()
            else:
                raise Exception("Lexing error")
        return token

    def __iter__(self):
        while True:
            token = self.next_token()
            if token: yield token
            else: break

    @classmethod
    def lex(cls, program):
        return list(cls(program))

class Parser(object):

    def __init__(self, lexer):
        self.lexer = lexer
        self.token = self.lexer.next_token()

    def error(self):
        raise Exception("Syntax error")

    def parse(self):
        return self.expr()

    def match(self, name):
        if list(self.token)[0] == name:
            self.token = self.lexer.next_token()
        else:
            self.error()

    def expr(self):
        node = self.term()
        while self.token and self.token.get("op") in {"+", "-"}:
            op = self.token["op"]
            self.match("op")
            node = {"type": "binop", "op": op, "left": node, "right": self.term()}
        return node

    def term(self):
        node = self.factor()
        while self.token and self.token.get("op") in {"*", "/"}:
            op = self.token["op"]
            self.match("op")
            node = {"type": "binop", "op": op, "left": node, "right": self.factor()}
        return node

    def factor(self):
        if "lparen" in self.token:
            self.match("lparen")
            node = self.expr()
            self.match("rparen")
            return node
        elif "num" in self.token:
            node = {"type": "term", "item": self.token["num"]}
            self.match("num")
            return node
        elif "id" in self.id:
            node = {"type": "term", "item": self.token["id"]}
            self.match("id")
            return node
        else:
            self.error()

def tree_eval(tree):
    if tree["type"] == "term":
        return tree["item"]
    elif tree["type"] == "binop":
        if tree["op"] == "*":
            return tree_eval(tree["left"]) * tree_eval(tree["right"])
        elif tree["op"] == "+":
            return tree_eval(tree["left"]) + tree_eval(tree["right"])
        else:
            raise Exception("Parsing error")

def interpret(program):
    lexer = Lexer(program)
    parser = Parser(lexer)
    tree = parser.parse()
    return tree_eval(tree)
