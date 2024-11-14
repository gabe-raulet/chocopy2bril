
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

class Interpreter(object):

    def __init__(self, program):
        self.program = program

    def evaluate(self):
        return eval(self.program)

    #  def evaluate_actual(self):
        #  tokens = Lexer.lex(self.program)
        #  tree = Parser.parse(tokens)
        #  result = self.compute(tree)
        #  return result

    @classmethod
    def interpret(cls, program):
        return cls(program).evaluate()
