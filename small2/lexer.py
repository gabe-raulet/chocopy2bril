import re
import sys
import json

class TokenPattern(object):

    def __init__(self, name, pattern, process=None):
        self.name = name
        self.pattern = pattern
        self.process = process

    @classmethod
    def lexemes(cls, name, lexemes, process=None):
        return cls(name, "|".join(map(re.escape, lexemes)), process)

    def match_text(self, text):
        m_obj = re.match(self.pattern, text)
        if m_obj:
            value = m_obj.group()
            if self.process: value = self.process(value)
            return value, text[m_obj.end():]
        else:
            return None

    def match_token(self, token):
        return re.match(self.pattern, token.lexeme()) is not None

class Token(object):

    BINOP = TokenPattern.lexemes("BINOP", ["+", "-", "*", "//", "%"])
    DELIM = TokenPattern.lexemes("DELIM", ["(", ")", ":", "="])
    TYPE  = TokenPattern.lexemes("TYPE", ["int"])
    KEYWORD = TokenPattern.lexemes("KEYWORD", ["print"])
    ID = TokenPattern("ID", r"[a-zA-Z][a-zA-Z_0-9]*")
    NUM = TokenPattern("NUM", r"[0-9]+", process=lambda x: int(x))

    SYMBOLS = [BINOP, DELIM, TYPE, KEYWORD]
    PATTERNS = [ID, NUM]

    def __init__(self, name, value=None):
        self.name = name
        self.value = value

    def lexeme(self):
        return self.value if self.value else self.name

    def __repr__(self):
        if self.value: return f"Token({self.name}, '{self.value}')"
        else: return f"Token('{self.name}')"

    def to_dict(self):
        if self.value: return {"name" : self.name, "value" : self.value}
        else: return {"symbol" : self.name}

    @classmethod
    def from_dict(cls, token_dict):
        if "symbol" in token_dict: return cls(token_dict["symbol"])
        else: return cls(token_dict["name"], token_dict["value"])

    @classmethod
    def match(cls, text):

        if not text:
            return None

        if text[0] == "\n":
            return cls("NEWLINE"), text[1:]

        text = text.lstrip()

        for symbol in cls.SYMBOLS:
            result = symbol.match_text(text)
            if result:
                value, remain = result
                return cls(value), remain

        for pattern in cls.PATTERNS:
            result = pattern.match_text(text)
            if result:
                value, remain = result
                return cls(pattern.name, value), remain

        return None

class Lexer(object):

    @staticmethod
    def _normalize_text(text):
        text = re.sub(r"[ \t]*#.*\n", r"\n", text) # remove comments
        text = re.sub(r"\n\n+", r"\n", text).strip() # remove consecutive newlines
        text = re.sub(r"[ \t]+\n", r"\n", text) # remove line-trailing whitespace
        text = re.sub(r"[ \t]+", r" ", text) # strip extra whitespace
        return text

    @staticmethod
    def _next_token(text):
        result = Token.match(text)
        if result: token, remain = result
        else: token, remain = None, ''
        return token, remain

    def __init__(self, text):
        self.token, self.text = Lexer._next_token(Lexer._normalize_text(text))

    def next_token(self):
        self.token, self.text = Lexer._next_token(self.text)
        return self.token

    def __iter__(self):
        while self.token:
            yield self.token
            self.next_token()
        yield Token("NEWLINE")

if __name__ == "__main__":
    #  json.dump([token.to_dict() for token in Lexer(sys.stdin.read())], sys.stdout, indent=4)
    for token in Lexer(sys.stdin.read()):
        print(token)

