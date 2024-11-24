import re
import sys
import json

class TokenClass(object):

    def __init__(self, name, pattern, lexemes=None, process=None):
        self.name = name # token class name
        self.pattern = pattern # regular substitution pattern
        self.lexemes = lexemes # exact-matching lexemes
        self.process = process # function to process string if not None

    def __repr__(self):
        return f"TokenClass(name={self.name}, pattern='{self.pattern}')"

    @classmethod
    def from_lexemes(cls, name, lexemes):
        return cls(name, "|".join(map(re.escape, lexemes)), lexemes)

    def match(self, text):
        m_obj = re.match(self.pattern, text)
        if m_obj:
            value = m_obj.group()
            if self.process: value = self.process(value)
            return (value, text[m_obj.end():])
        else:
            return None

class Token(object):

    BINOP   = TokenClass.from_lexemes("BINOP", ["+", "-", "*", "//", "%", "==", "!=", "<=", ">=", "<", ">"])
    DELIM   = TokenClass.from_lexemes("DELIM", ["(", ")", ":", ",", ".", "->", "="])
    TYPE    = TokenClass.from_lexemes("TYPE", ["int", "bool"])
    KEYWORD = TokenClass.from_lexemes("KEYWORD", ["if", "elif", "else", "while"])
    PRINT   = TokenClass.from_lexemes("PRINT", ["print"])
    BOOL    = TokenClass.from_lexemes("BOOL", ["True", "False"])

    ID      = TokenClass("ID", r"[a-zA-Z_][a-zA-Z_0-9]*")
    NUM     = TokenClass("NUM", r"[0-9]+", process=lambda x: int(x))

    TOKENS = [BINOP, DELIM, TYPE, KEYWORD, PRINT, BOOL, ID, NUM]

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        if isinstance(self.value, str): return f"Token(name={self.name}, value='{self.value}')"
        else: return f"Token(name={self.name}, value={self.value})"

    def to_dict(self):
        return {"name" : self.name, "value" : self.value}

    @classmethod
    def from_dict(cls, token_dict):
        return cls(token_dict["name"], token_dict["value"])

    @classmethod
    def newline_token(cls):
        return cls("NEWLINE", None)

    @classmethod
    def match(cls, text):

        if not text:
            return None

        if text.startswith("\n"):
            return cls.newline_token(), text[1:]

        text = text.lstrip()

        for token in cls.TOKENS:
            result = token.match(text)
            if result:
                value, remain = result
                return cls(token.name, value), remain

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
        yield Token.newline_token()

if __name__ == "__main__":
    json.dump([token.to_dict() for token in Lexer(sys.stdin.read())], sys.stdout, indent=4)
