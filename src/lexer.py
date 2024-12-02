import re
import sys
import json

class TokenPattern(object):

    def __init__(self, name, pattern, process):
        self.name = name
        self.pattern = pattern
        self.process = process

    def __repr__(self):
        return f"TokenPattern({self.name}, '{self.pattern}')"

    @classmethod
    def exact(cls, name, lexeme, process=None):
        return cls(name, re.escape(lexeme), process)

    @classmethod
    def regexp(cls, name, pattern, process=None):
        return cls(name, pattern, process)

    @classmethod
    def group(cls, name, token_patterns, process=None):
        return cls(name, "|".join(t.pattern for t in token_patterns), process)

    def match(self, text):
        return re.match(self.pattern, text) is not None

    def lex_and_split(self, text):
        m_obj = re.match(self.pattern, text)
        if m_obj:
            value = m_obj.group()
            if self.process: value = self.process(value)
            return value, text[m_obj.end():]
        else:
            return None

class Token(object):

    PRECEDENCE = { "OR" : 2,
                  "AND" : 3,
                  "NOT" : 4,
                   "EQ" : 5,  "NE" : 5,  "LT" : 5, "GT" : 5, "LE" : 5, "GE" : 5,
                  "ADD" : 6, "SUB" : 6,
                  "MUL" : 7, "DIV" : 7, "MOD" : 7,
                 "USUB" : 8}

    @staticmethod
    def get_precedence(op):
        return Token.PRECEDENCE.get(op, -float('inf'))

    OR = TokenPattern.exact("OR", "or")
    AND = TokenPattern.exact("AND", "and")
    NOT = TokenPattern.exact("NOT", "not")
    EQ = TokenPattern.exact("EQ", "==")
    NE = TokenPattern.exact("NE", "!=")
    LT = TokenPattern.exact("LT", "<")
    GT = TokenPattern.exact("GT", ">")
    LE = TokenPattern.exact("LE", "<=")
    GE = TokenPattern.exact("GE", ">=")
    ADD = TokenPattern.exact("ADD", "+")
    SUB = TokenPattern.exact("SUB", "-")
    MUL = TokenPattern.exact("MUL", "*")
    DIV = TokenPattern.exact("DIV", "//")
    MOD = TokenPattern.exact("MOD", "%")

    LPAREN = TokenPattern.exact("LPAREN", "(")
    RPAREN = TokenPattern.exact("RPAREN", ")")
    COLON  = TokenPattern.exact("COLON", ":")
    ASSIGN = TokenPattern.exact("ASSIGN", "=")
    ARROW  = TokenPattern.exact("ARROW", "->")
    COMMA  = TokenPattern.exact("COMMA", ",")

    KEYWORD = TokenPattern.regexp("KEYWORD", r"print|def|return")
    TYPE    = TokenPattern.regexp("TYPE", r"int|bool")
    BOOL    = TokenPattern.regexp("BOOL", r"True|False", process=lambda v: {"True" : True, "False" : False}[v])

    ID      = TokenPattern.regexp("ID", r"[a-zA-Z_][a-zA-Z_0-9]*")
    NUM     = TokenPattern.regexp("NUM", r"[0-9]+", process=lambda v: int(v))

    GROUP1 = [EQ, NE, LE, GE, ARROW]
    GROUP2 = [LT, GT, ADD, SUB, MUL, DIV, MOD, NOT, AND, OR, LPAREN, RPAREN, COLON, ASSIGN, COMMA]

    G1 = TokenPattern.group("G1", GROUP1)
    G2 = TokenPattern.group("G2", GROUP2)

    def __init__(self, name, value=None):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"Token({self.name}, '{self.value}')"

    def _matches(self, other):
        if isinstance(other, str): pass
        elif isinstance(other, (Token, TokenPattern)): other = other.name
        else: raise Exception()
        return self.name == other

    def matches(self, other):
        if not isinstance(other, (list, tuple)): other = [other]
        for o in other:
            if self._matches(o):
                return True
        return False

    @classmethod
    def match(cls, text):

        if not text:
            return None

        text = text.lstrip()

        if cls.G1.match(text):
            for op in cls.GROUP1:
                if op.match(text):
                    value, text = op.lex_and_split(text)
                    return Token(op.name, value), text

        if cls.G2.match(text):
            for op in cls.GROUP2:
                if op.match(text):
                    value, text = op.lex_and_split(text)
                    return Token(op.name, value), text

        if cls.BOOL.match(text):
            value, text = cls.BOOL.lex_and_split(text)
            return Token(cls.BOOL.name, value), text

        if cls.TYPE.match(text):
            value, text = cls.TYPE.lex_and_split(text)
            return Token(cls.TYPE.name, value), text

        if cls.KEYWORD.match(text):
            value, text = cls.KEYWORD.lex_and_split(text)
            return Token(cls.KEYWORD.name, value), text

        if cls.ID.match(text):
            value, text = cls.ID.lex_and_split(text)
            return Token(cls.ID.name, value), text

        if cls.NUM.match(text):
            value, text = cls.NUM.lex_and_split(text)
            return Token(cls.NUM.name, value), text

        return None

def lex_text(text):
    stack = [0]
    while True:
        s = re.search(r"[ \t]*(#.*)?\n", text)
        if not s: break
        line = text[:s.start()]
        text = text[s.end():]
        if not line: continue
        front = re.match(r"[ ]*", line)
        l = len(front.group())
        if l > stack[-1]:
            stack.append(l)
            yield Token("INDENT")
        elif l < stack[-1]:
            while l < stack[-1]:
                stack.pop()
                yield Token("DEDENT")
            assert l == stack[-1]
        result = Token.match(line)
        while result:
            token, line = result
            yield token
            result = Token.match(line)
        yield Token("NEWLINE")

