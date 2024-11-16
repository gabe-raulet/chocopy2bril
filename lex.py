import sys
import json
from collections import namedtuple

Token = namedtuple("Token", ["name", "value"])

PLUS = "PLUS"
MINUS = "MINUS"
MUL = "MUL"
DIV = "DIV"
LPAREN = "LPAREN"
RPAREN = "RPAREN"
ASSIGN = "ASSIGN"
ID = "ID"
NUM = "NUM"
NEWLINE = "NEWLINE"
PRINT = "PRINT"

char_tokens = {"+" : PLUS,
               "-" : MINUS,
               "*" : MUL,
               "(" : LPAREN,
               ")" : RPAREN,
               "=" : ASSIGN,
               "\n": NEWLINE}

class Lexer(object):

    def __init__(self, program):
        self.program = program
        self.size = len(self.program)
        self.pos = 0
        self.cur = self.program[self.pos]

    def error(self):
        raise Exception("Lexing error")

    def advance(self):
        if self.pos + 1 < self.size:
            self.pos += 1
            self.cur = self.program[self.pos]
        else:
            self.cur = None

    def cur_is_whitespace(self):
        """
        Whitespace does not include the newline character, as we
        need to use that as a token to separate consecutive statements
        """
        return self.cur.isspace() and self.cur != "\n"

    def cur_is_digit(self):
        return self.cur.isdigit()

    def cur_is_letter(self):
        return self.cur.isalpha() or self.cur == "_"

    def cur_is_letter_or_digit(self):
        return self.cur_is_digit() or self.cur_is_letter()

    def skip_whitespace(self):
        while self.cur and self.cur_is_whitespace():
            self.advance()

    def attempt_match(self, word):
        n = len(word)
        i = 0
        while i + self.pos < self.size and i < n:
            if word[i] != self.program[i + self.pos]:
                return False
            i += 1
        if i < n or (i + self.pos < self.size and not self.program[i + self.pos].isspace()):
            return False
        self.pos += i
        self.cur = self.program[self.pos]
        return True

    def number(self):
        """
        A number token is a string of digits that does NOT begin
        with a zero '0'.
        """
        if self.cur == "0": self.error()
        digits = []
        while self.cur and self.cur_is_digit():
            digits.append(self.cur)
            self.advance()
        return int("".join(digits))

    def identifier(self):
        """
        An identifier is the following: letter(letter|digit)*
        where letter := [a-zA-Z_] and digit := [0-9]
        """
        if not self.cur_is_letter(): self.error()
        chars = [self.cur]
        self.advance()
        while self.cur and self.cur_is_letter_or_digit():
            chars.append(self.cur)
            self.advance()
        return "".join(chars)

    def next_token(self):
        self.skip_whitespace()
        token = None
        if self.cur:
            if self.cur.isdigit():
                token = Token(name=NUM, value=self.number())
            elif self.cur_is_letter():
                if self.attempt_match("print"):
                    token = Token(name=PRINT, value="print")
                else:
                    token = Token(name=ID, value=self.identifier())
            elif self.cur in char_tokens:
                token = Token(name=char_tokens[self.cur], value=None)
                self.advance()
            else:
                raise Exception("Lexing error")
        return token

    def __iter__(self):
        token = self.next_token()
        while token:
            yield token
            token = self.next_token()

def token_to_dict(token):
    return {token.name : token.value}

if __name__ == "__main__":
    program = sys.stdin.read()
    lexer = Lexer(program)
    tokens = [token_to_dict(token) for token in lexer]
    json.dump(tokens, sys.stdout, indent=4)
