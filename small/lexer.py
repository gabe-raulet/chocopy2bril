import re
import sys
import json

class TokenClass(object):

    def __init__(self, name, pattern, lexemes=None, process=None):
        self.name = name
        self.pattern = pattern
        self.lexemes = lexemes
        self.process = process

    def __repr__(self):
        return f"TokenClass(name={self.name}, pattern={self.pattern})"

    def match(self, text):
        m_obj = re.match(self.pattern, text)
        if m_obj:
            value = m_obj.group()
            lexname = None if not self.lexemes else self.lexemes[value]
            if self.process: value = self.process(value)
            return (lexname, value, text[m_obj.end():])
        else:
            return None

    @classmethod
    def from_lexemes(cls, name, lexemes):
        return cls(name, "|".join(map(re.escape, list(lexemes.keys()))), lexemes)

    @classmethod
    def BINOP(cls):
        lexemes = {"+" : "ADD", "-" : "SUB", "*" : "MUL", "//" : "DIV", "%" : "MOD", "==" : "EQ", "!=" : "NE", "<=" : "LE", ">=" : "GE", "<" : "LT", ">" : "GT"}
        return cls.from_lexemes("BINOP", lexemes)

    @classmethod
    def DELIM(cls):
        lexemes = {"(" : "LPAREN", ")" : "RPAREN", ":" : "COLON", "," : "COMMA", "." : "DOT", "->" : "ARROW", "=" : "ASSIGN"}
        return cls.from_lexemes("DELIM", lexemes)

class Token(object):

    BINOP   = TokenClass.BINOP()
    DELIM   = TokenClass.DELIM()

    TYPE    = TokenClass("TYPE", "int|bool")
    KEYWORD = TokenClass("KEYWORD", "if|elif|else|while")
    PRINT   = TokenClass("PRINT", "print")
    BOOL    = TokenClass("BOOL", "True|False")
    ID      = TokenClass("ID", r"[a-zA-Z_][a-zA-Z_0-9]*")
    NUM     = TokenClass("NUM", r"[0-9]+", process=lambda x: int(x))

    TOKENS = [BINOP, DELIM, TYPE, KEYWORD, PRINT, BOOL, ID, NUM]

    def __init__(self, name, value, lexeme):
        self.name = name
        self.value = value
        self.lexeme = lexeme

    def __repr__(self):
        return f"Token(name={self.name}, value={self.value}, lexeme={self.lexeme})"

    def to_dict(self):
        return {"name" : self.name, "value" : self.value, "lexeme" : self.lexeme}

    @classmethod
    def from_dict(self, token_dict):
        return cls(token_dict["name"], token_dict["value"], token_dict["lexeme"])

    @classmethod
    def match(cls, text):
        if not text: return None
        if text[0] == "\n": return cls("NEWLINE", None, r"\n"), text[1:]
        text = text.lstrip()
        for token in cls.TOKENS:
            result = token.match(text)
            if result:
                lexname, lexeme, remain = result
                return cls(token.name, lexname, lexeme), remain
        return None

class Lexer(object):

    @staticmethod
    def normalize_text(text):
        text = re.sub(r"[ \t]*#.*\n", r"\n", text) # remove comments
        text = re.sub(r"\n\n+", r"\n", text).strip() # remove consecutive newlines
        text = re.sub(r"[ \t]+\n", r"\n", text) # remove line-trailing whitespace
        text = re.sub(r"[ \t]+", r" ", text) # strip extra whitespace
        return text

    def __init__(self, text):
        self.text = Lexer.normalize_text(text)
        self.peek = self.token = None
        self.next_token()
        self.token = self.peek
        self.next_token()

    def next_token(self):
        self.token = self.peek
        t = Token.match(self.text)
        if t: self.peek, self.text = t
        else: self.peek = None
        return self.token

    def peek_token(self):
        return self.peek

    def __iter__(self):
        while self.token:
            yield self.token
            self.next_token()
        yield Token("NEWLINE", None, r"\n")

if __name__ == "__main__":
    text = sys.stdin.read()
    tokens = [token.to_dict() for token in Lexer(text)]
    json.dump(tokens, sys.stdout, indent=4)
