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

    ADD = TokenPattern.exact("ADD", "+")
    SUB = TokenPattern.exact("SUB", "-")
    MUL = TokenPattern.exact("MUL", "-")
    DIV = TokenPattern.exact("DIV", "//")
    MOD = TokenPattern.exact("MOD", "%")

    LPAREN = TokenPattern.exact("LPAREN", "(")
    RPAREN = TokenPattern.exact("RPAREN", ")")
    COLON  = TokenPattern.exact("COLON", ":")
    ASSIGN = TokenPattern.exact("ASSIGN", "=")

    PRINT = TokenPattern.exact("PRINT", "print")

    TYPE = TokenPattern.regexp("TYPE", r"int|bool|str")
    ID   = TokenPattern.regexp("ID", r"[a-zA-Z_][a-zA-Z_0-9]*")
    NUM  = TokenPattern.regexp("NUM", r"[0-9]+", process=lambda v: int(v))

    BINOP_GROUP = [ADD, SUB, MUL, DIV, MOD]
    DELIM_GROUP = [LPAREN, RPAREN, COLON, ASSIGN]
    KEYWORD_GROUP = [PRINT]
    EXACT_GROUP = [BINOP_GROUP, DELIM_GROUP, KEYWORD_GROUP]

    BINOP = TokenPattern.group("BINOP", BINOP_GROUP)
    DELIM = TokenPattern.group("DELIM", DELIM_GROUP)
    KEYWORD = TokenPattern.group("KEYWORD", KEYWORD_GROUP)

    def __init__(self, name, value=None):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"Token({self.name}, '{self.value}')"

    def to_dict(self):
        return {"name" : self.name, "value" : self.value}

    @classmethod
    def from_dict(cls, token_dict):
        return cls(token_dict["name"], token_dict["value"])

    @classmethod
    def match(cls, text):

        if not text:
            return None

        text = text.lstrip()

        if cls.BINOP.match(text):
            for binop in cls.BINOP_GROUP:
                if binop.match(text):
                    value, text = binop.lex_and_split(text)
                    return Token(binop.name, value), text

        if cls.DELIM.match(text):
            for delim in cls.DELIM_GROUP:
                if delim.match(text):
                    value, text = delim.lex_and_split(text)
                    return Token(delim.name, value), text

        if cls.KEYWORD.match(text):
            for keyword in cls.KEYWORD_GROUP:
                if keyword.match(text):
                    value, text = keyword.lex_and_split(text)
                    return Token(keyword.name, value), text

        if cls.TYPE.match(text):
            value, text = cls.TYPE.lex_and_split(text)
            return Token(cls.TYPE.name, value), text

        if cls.ID.match(text):
            value, text = cls.ID.lex_and_split(text)
            return Token(cls.ID.name, value), text

        if cls.NUM.match(text):
            value, text = cls.NUM.lex_and_split(text)
            return Token(cls.NUM.name, value), text

        return None

def lex_text(text):
    while True:
        s = re.search(r"[ \t]*(#.*)?\n", text)
        if not s: break
        line = text[:s.start()]
        text = text[s.end():]
        if not line: continue
        result = Token.match(line)
        while result:
            token, line = result
            yield token
            result = Token.match(line)
        yield Token("NEWLINE")

if __name__ == "__main__":
    json.dump([token.to_dict() for token in lex_text(sys.stdin.read())], sys.stdout, indent=4)

    #  for token in lex_text(sys.stdin.read()):
        #  print(token)
