import sys

class Token(object):

    ADD     = "ADD"     # '+'
    SUB     = "SUB"     # '-'
    MUL     = "MUL"     # '*'
    DIV     = "DIV"     # '/'
    MOD     = "MOD"     # '%'
    LPAREN  = "LPAREN"  # '('
    RPAREN  = "RPAREN"  # ')'
    ASSIGN  = "ASSIGN"  # '='
    COLON   = "COLON"   # ':'
    COMMA   = "COMMA"   # ','
    NEWLINE = "NEWLINE" # '\n'

    ID  = "ID"  # [a-zA-Z_]
    NUM = "NUM" # [1-9][0-9]*

    PRINT = "PRINT" # 'print'
    RET   = "RET"   # 'return'
    BOOL  = "BOOL"  # 'bool'
    INT   = "INT"   # 'int'
    TRUE  = "TRUE"  # 'True'
    FALSE = "FALSE" # 'False'
    IF    = "IF"    # 'if'
    ELIF  = "ELIF"  # 'elif'
    ELSE  = "ELSE"  # 'else'
    FOR   = "FOR"   # 'for'
    WHILE = "WHILE" # 'while'
    NOT   = "NOT"   # 'not'
    AND   = "AND"   # 'and'
    OR    = "OR"    # 'or'

    EQ = "EQ" # '=='
    NE = "NE" # '!='
    LT = "LT" # '<'
    GT = "GT" # '>'
    LE = "LE" # '<='
    GE = "GE" # '>='

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        value = self.value if self.name != Token.NEWLINE else "\\n"
        return f"Token({self.name}, \"{value}\")"

    def as_dict(self):
        return {"name" : self.name, "value" : self.value}

class Lexer(object):

    def __init__(self, prog):
        self.prog = prog
        self.size = len(prog)
        self.pos = 0
        self.cur = self.prog[self.pos]

    def reset(self):
        self.pos = 0
        self.cur = self.prog[self.pos]

    def error(self):
        raise Exception("Lexing error")

    def advance(self, amt=1):
        if self.pos + amt < self.size:
            self.pos += amt
            self.cur = self.prog[self.pos]
        else:
            self.cur = None

    @staticmethod
    def program_whitespace(char):
        """
        Whitespace does not include the newline character, as we
        need to use that as a token to separate consecutive statements
        """
        return char.isspace() and char != "\n"

    def cur_is_whitespace(self):
        return self.program_whitespace(self.cur)

    def cur_is_digit(self):
        return self.cur.isdigit()

    def cur_is_letter(self):
        return self.cur.isalpha() or self.cur == "_"

    def cur_is_letter_or_digit(self):
        return self.cur_is_digit() or self.cur_is_letter()

    def cur_is_term_token(self):
        return self.cur in ("=","!", "<", ">", "+", "-", "*", "/", "(", ")", ":", "%", "\n")

    def skip_whitespace(self):
        while self.cur and self.cur_is_whitespace():
            self.advance()

    def attempt_match(self, word):
        if self.prog[self.pos:self.pos+len(word)] != word:
            return False
        else:
            self.advance(len(word))
            return True

    def number(self):
        """
        A number token is a string of digits that does NOT begin
        with a zero '0', unless it is supposed to be zero.
        """
        digits = []
        while self.cur and self.cur_is_digit():
            digits.append(self.cur)
            self.advance()
        if digits[0] == "0" and len(digits) > 1:
            self.error()
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
                token = Token(Token.NUM, self.number())
            elif self.cur_is_letter():
                if   self.attempt_match("print"):  token = Token(Token.PRINT, "print")
                elif self.attempt_match("return"): token = Token(Token.RET, "return")
                elif self.attempt_match("bool"):   token = Token(Token.BOOL, "bool")
                elif self.attempt_match("int"):    token = Token(Token.INT, "int")
                elif self.attempt_match("True"):   token = Token(Token.TRUE, "True")
                elif self.attempt_match("False"):  token = Token(Token.FALSE, "False")
                elif self.attempt_match("if"):     token = Token(Token.IF, "if")
                elif self.attempt_match("elif"):   token = Token(Token.ELIF, "elif")
                elif self.attempt_match("else"):   token = Token(Token.ELSE, "else")
                elif self.attempt_match("for"):    token = Token(Token.FOR, "for")
                elif self.attempt_match("while"):  token = Token(Token.WHILE, "while")
                elif self.attempt_match("not"):    token = Token(Token.NOT, "not")
                elif self.attempt_match("and"):    token = Token(Token.AND, "and")
                elif self.attempt_match("or"):     token = Token(Token.OR, "or")
                else: token = Token(Token.ID, self.identifier())
            elif self.cur_is_term_token():
                if   self.attempt_match("=="): token = Token(Token.EQ, "==")
                elif self.attempt_match("!="): token = Token(Token.NE, "!=")
                elif self.attempt_match("<="): token = Token(Token.LE, "<=")
                elif self.attempt_match(">="): token = Token(Token.GE, ">=")
                elif self.attempt_match(">"):  token = Token(Token.GT, ">")
                elif self.attempt_match("<"):  token = Token(Token.LT, "<")
                elif self.attempt_match("+"):  token = Token(Token.ADD, "+")
                elif self.attempt_match("-"):  token = Token(Token.SUB, "-")
                elif self.attempt_match("*"):  token = Token(Token.MUL, "*")
                elif self.attempt_match("/"):  token = Token(Token.DIV, "/")
                elif self.attempt_match("%"):  token = Token(Token.MOD, "%")
                elif self.attempt_match("("):  token = Token(Token.LPAREN, "(")
                elif self.attempt_match(")"):  token = Token(Token.RPAREN, ")")
                elif self.attempt_match(":"):  token = Token(Token.COLON, ":")
                elif self.attempt_match("="):  token = Token(Token.ASSIGN, "=")
                elif self.attempt_match("\n"): token = Token(Token.NEWLINE, "\n")
            else:
                self.error()
        return token

    def __iter__(self):
        token = self.next_token()
        while token:
            yield token
            token = self.next_token()

if __name__ == "__main__":
    tokens = [token.as_dict() for token in Lexer(sys.stdin.read())]
    for token in tokens:
        print(token)
    #  for token in lexer:
        #  print(token)
