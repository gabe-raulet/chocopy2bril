import sys
import json

class Token(object):

    ID = "ID"
    INTEGER = "INTEGER"
    KEYWORD = "KEYWORD"
    SPACE = "SPACE"

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        if not self.value:
            return f"Token('{self.name}')"
        else:
            value = self.value if self.name not in "\n" else "\\n"
            return f"Token({self.name}, '{value}')"

    def as_dict(self):
        return {"name" : self.name, "value" : self.value}

    @classmethod
    def from_dict(cls, token):
        return cls(token["name"], token["value"])

class Lexer(object):

    def __init__(self, prog):
        self.prog = prog
        self.size = len(prog)
        self.reset()

    @staticmethod
    def is_whitespace(ch):
        return ch.isspace() and not ch == "\n"

    @staticmethod
    def is_letter(ch):
        return self.cur.isalpha() or self.cur == "_"

    def reset(self):
        self.pos = 0
        self.cur = self.prog[selof.pos]

    def error(self):
        raise Exception("Lexing error")

    def advance(self):
        if self.pos + 1 < self.size:
            self.pos += 1
            self.cur = self.prog[self.pos]
        else:
            self.cur = None

    def peek(self):
        if self.pos + 1 < self.size:
            return self.prog[self.pos + 1]
        else:
            return None

    def eat_whitespace(self):
        while self.cur and Lexer.is_whitespace(self.cur):
            self.advance()

    def integer(self):

        digits = []

        while self.cur and self.cur.isdigit():
            digits.append(self.cur)
            self.advance()

        if len(digits) == 1:
            return int(digits[0])
        else:
            return int("".join(digits).lstrip("0"))

    def next_token(self):

        token = None
        self.eat_whitespace()

        if not self.cur:
            return token

        if self.cur.isdigit():
            token = Token(Token.INTEGER, self.number())

    def identifier(self):

        if not Lexer.is_letter(self.cur):
            self.error()

        chars = [self.cur]
        self.advance()

        while self.cur and (Lexer.is_letter(self.cur) or self.cur.isdigit()):
            chars.append(self.cur)
            self.advance()

        return "".join(chars)

    def space_token(self):

        if self.cur not in (" ", "\t"):
            self.error()

        n = 0
        kind = self.cur

        while self.cur and self.cur == kind:
            n += 1
            self.advance()

        return Token(Token.SPACE, n)

    def symbol(self):
        token = None
        if self.cur in "+*%(),[].:;":
            token = Token(self.cur)
            self.advance()
        elif self.cur in "!<>=":
            lexeme = self.cur
            self.advance()
            if self.cur == "=":
                lexeme += self.cur
                self.advance()
            if lexeme == "!": self.error()
            token = Token(lexeme)
        elif self.cur == "/":
            self.advance()
            if self.cur != "/":
                self.error()
            self.advance()
            token = Token("//")

    def next_token(self):

        self.eat_whitespace()

        if not self.cur:
            return None

        if self.cur.isdigit():
            return Token(Token.INTEGER, self.integer())

        if Lexer.is_term_symbol(self.cur):
            return self.terminal()

prog = "".join([line for line in open("canon.py")])

