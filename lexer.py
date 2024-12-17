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
                  "MUL" : 7, "DIV" : 7, "MOD" : 7}

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

    KEYWORD = TokenPattern.regexp("KEYWORD", r"print|def|return|None|pass|if|elif|else|while|for|in|range")
    TYPE    = TokenPattern.regexp("TYPE", r"int|bool")
    BOOL    = TokenPattern.regexp("BOOL", r"True|False", process=lambda v: {"True" : True, "False" : False}[v])

    ID      = TokenPattern.regexp("ID", r"[a-zA-Z_][a-zA-Z_0-9]*")
    NUM     = TokenPattern.regexp("NUM", r"[0-9]+", process=lambda v: int(v))

    LEXEMES_GROUP = [EQ, LE, GE, ARROW, NE, LT, GT, ADD, SUB, MUL, DIV, MOD, NOT, AND, OR, LPAREN, RPAREN, COLON, ASSIGN, COMMA]
    LEXEMES = TokenPattern.group("LEXEMES", LEXEMES_GROUP)

    def __init__(self, name, value=None):
        self.name = name # token category
        self.value = value # token value (actual string); NEWLINE, INDENT and DEDENT tokens have value=None

    def __repr__(self):
        return f"Token({self.name}, '{self.value}')"

    def to_dict(self):
        return {"name" : self.name, "value" : self.value}

    @classmethod
    def from_dict(cls, token):
        return cls(token.get("name"), token.get("value"))

    def _matches(self, other):
        if isinstance(other, str): pass
        elif isinstance(other, (Token, TokenPattern)): other = other.name
        else: raise Exception()
        return self.name == other

    def matches(self, other):
        """
        Returns true if this token "matches" `other` (or any token in `other` if it is a tuple/list).
        A token "matches" another token if their token "names" are equal.
        """
        if not isinstance(other, (list, tuple)): other = [other]
        for o in other:
            if self._matches(o):
                return True
        return False

    @classmethod
    def match(cls, text):

        """
        Given a string `text`, compute the first matching token of the text (if there is one),
        and return a pair consisting of (1) the matched token and (2) the remainder of `text`
        after the matched token. If no text remains, or no token can be matched, return None.
        """

        if not text:
            return None

        text = text.lstrip()

        """
        Start by checking (in order!) if we match the following "exact match" terminals:

            '==', # check before '='
            '<=', # check before '<'
            '>=', # check before '>'
            '->', # check before '-'

            '!=', '<', '>', '+', '-', '*', '//', '%', 'not', 'and', 'or', '(', ')', ':', '=', ','
        """
        if cls.LEXEMES.match(text):
            for op in cls.LEXEMES_GROUP:
                if op.match(text):
                    value, text = op.lex_and_split(text)
                    return Token(op.name, value), text

        """
        Check for BOOL terminal: 'True' | 'False'
        """
        if cls.BOOL.match(text):
            value, text = cls.BOOL.lex_and_split(text)
            return Token(cls.BOOL.name, value), text

        """
        Check for TYPE terminal: 'int' | 'bool'
        """
        if cls.TYPE.match(text):
            value, text = cls.TYPE.lex_and_split(text)
            return Token(cls.TYPE.name, value), text

        """
        Check for KEYWORD terminal: 'print' | 'def' | 'return' | 'pass' | 'if' | 'elif' | 'else' | 'while' | 'for' | 'in' | 'range'
        """
        if cls.KEYWORD.match(text):
            value, text = cls.KEYWORD.lex_and_split(text)
            return Token(cls.KEYWORD.name, value), text

        """
        Check for ID terminal: [a-zA-Z_][a-zA-Z_0-9]*
        """
        if cls.ID.match(text):
            value, text = cls.ID.lex_and_split(text)
            return Token(cls.ID.name, value), text

        """
        Check for NUM terminal: [0-9]+
        """
        if cls.NUM.match(text):
            value, text = cls.NUM.lex_and_split(text)
            return Token(cls.NUM.name, value), text

        return None

def lex_text(text):

    stack = [0] # indentation level stack

    # each iteration is for a new program line
    while True:

        if text.startswith("#!#"):
            break # skip code after #!# appears

        # find the first ignorable character on current line
        s = re.search(r"[ \t]*(#.*)?\n", text)

        if not s:
            break # nothing left, we're done

        line = text[:s.start()] # line of interest
        text = text[s.end():] # remaining text

        if not line:
            continue # empty line, go to next one

        # match leading whitespace
        front = re.match(r"[ ]*", line)
        l = len(front.group())

        if l > stack[-1]:
            stack.append(l) # more whitespace than last line means we are indenting
            yield Token("INDENT")
        elif l < stack[-1]: # less whitespace than last line means we are dedenting
            while l < stack[-1]:
                stack.pop()
                yield Token("DEDENT")
            assert l == stack[-1]

        # tokenize the line
        result = Token.match(line)
        while result:
            token, line = result
            yield token
            result = Token.match(line)

        # end of line token
        yield Token("NEWLINE")

    # handle remaining dedents
    while stack and stack[-1] > 0:
        stack.pop()
        yield Token("DEDENT")

def lexer_main(pretty=False):
    tokens = list(lex_text(sys.stdin.read()))
    if pretty:
        for token in tokens:
            print(token)
    else:
        json.dump(list(map(lambda t: t.to_dict(), tokens)), sys.stdout, indent=4)

if __name__ == "__main__":
    lexer_main("-p" in sys.argv)
