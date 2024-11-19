import sys

class Token(object):

    PLUS    = "PLUS"
    MINUS   = "MINUS"
    MUL     = "MUL"
    DIV     = "DIV"
    LPAREN  = "LPAREN"
    RPAREN  = "RPAREN"
    ASSIGN  = "ASSIGN"
    ID      = "ID"
    NUM     = "NUM"
    NEWLINE = "NEWLINE"
    PRINT   = "PRINT"

    char_tokens = {"+" : PLUS,
                   "-" : MINUS,
                   "*" : MUL,
                   "/" : DIV,
                   "(" : LPAREN,
                   ")" : RPAREN,
                   "=" : ASSIGN,
                   "\n": NEWLINE}

    token_chars = {PLUS    : "+",
                   MINUS   : "-",
                   MUL     : "*",
                   DIV     : "/",
                   LPAREN  : "(",
                   RPAREN  : ")",
                   ASSIGN  : "=",
                   NEWLINE : "\n"}

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"Token({self.name}, {self.value})"

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
        while self.pos + i < self.size and i < n:
            if word[i] != self.program[self.pos + i]:
                return False
            i += 1
        if i < n or (self.pos + i < self.size and not self.program[self.pos + i].isspace()):
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
                token = Token(Token.NUM, self.number())
            elif self.cur_is_letter():
                if self.attempt_match("print"):
                    token = Token(Token.PRINT, "print")
                else:
                    token = Token(Token.ID, self.identifier())
            elif self.cur in Token.char_tokens:
                token = Token(Token.char_tokens[self.cur], self.cur)
                self.advance()
            else:
                raise Exception("Lexing error")
        return token

    def __iter__(self):
        token = self.next_token()
        while token:
            yield token
            token = self.next_token()

class Ast(object):
    pass

class AstBody(Ast):

    def __init__(self, first_stmt):
        self.stmts = [first_stmt]

    def __iter__(self):
        for stmt in self.stmts:
            yield stmt

    def append_stmt(self, stmt):
        self.stmts.append(stmt)

    def __repr__(self):
        indent = " " * 4
        n = len(self.stmts)
        rep = "AstBody\n([\n"
        for i in range(n-1):
            rep += f"{indent}{self.stmts[i]},\n"
        rep += f"{indent}{self.stmts[-1]}\n"
        rep += "])"
        return rep

class AstAssign(Ast):

    def __init__(self, target, expr):
        self.target = target
        self.expr = expr

    def __repr__(self):
        return f"AstAssign(target={self.target}, expr={self.expr})"

class AstPrint(Ast):

    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"AstPrint(expr={self.expr})"

class AstTerm(Ast):

    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return f"AstTerm({self.token})"

class AstBinOp(Ast):

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"AstBinOp(op={self.op}, left={self.left}, right={self.right})"

class Parser(object):

    def __init__(self, tokens):
        self.tokens = tokens
        self.size = len(self.tokens)
        self.pos = 0
        self.token = self.tokens[self.pos]

    def error(self):
        raise Exception("Syntax error")

    def advance(self):
        if self.pos + 1 < self.size:
            self.pos += 1
            self.token = self.tokens[self.pos]
        else:
            self.token = None

    def peek(self):
        if self.pos + 1 < self.size:
            return self.tokens[self.pos + 1]
        else:
            return None

    def match(self, token_name):
        if self.token.name == token_name:
            self.advance()
        else:
            self.error()

    def parse(self):
        return self.stmts()

    def stmts(self):
        body = AstBody(self.stmt())
        while self.token: body.append_stmt(self.stmt())
        return body

    def stmt(self):
        node = None
        if self.token.name == Token.PRINT:
            self.match(Token.PRINT)
            node = AstPrint(expr=self.expr())
        elif self.token.name == Token.ID and self.peek().name == Token.ASSIGN:
            target = self.token
            self.match(Token.ID)
            self.match(Token.ASSIGN)
            node = AstAssign(target=target, expr=self.expr())
        else:
            node = self.expr()

        if self.token.name == Token.NEWLINE:
            self.match(Token.NEWLINE)

        return node

    def expr(self):
        node = self.term()
        while self.token and self.token.name in {Token.PLUS, Token.MINUS}:
            op = self.token.name
            self.match(op)
            node = AstBinOp(op=op, left=node, right=self.term())
        return node

    def term(self):
        node = self.factor()
        while self.token and self.token.name in {Token.MUL, Token.DIV}:
            op = self.token.name
            self.match(op)
            node = AstBinOp(op=op, left=node, right=self.factor())
        return node

    def factor(self):
        if self.token.name == Token.LPAREN:
            self.match(Token.LPAREN)
            node = self.expr()
            self.match(Token.RPAREN)
            return node
        elif self.token.name == Token.NUM:
            node = AstTerm(self.token)
            self.match(Token.NUM)
            return node
        elif self.token.name == Token.ID:
            node = AstTerm(self.token)
            self.match(Token.ID)
            return node
        else:
            self.error()

class CodeGenerator(object):

    def __init__(self, root):
        self.root = root
        self.reg = 0
        self.stack = []
        self.instrs = []

    def fresh_reg(self):
        vr = f"_t{self.reg}"
        self.reg += 1
        return vr

    def traverse(self, node):
        if isinstance(node, AstTerm):
            reg = self.fresh_reg()
            self.instrs.append(f"{reg} := {node.token.value}")
            self.stack.append(reg)
        elif isinstance(node, AstBinOp):
            self.traverse(node.left)
            self.traverse(node.right)
            rhs = self.stack.pop()
            lhs = self.stack.pop()
            reg = self.fresh_reg()
            self.instrs.append(f"{reg} := {lhs} {Token.token_chars[node.op]} {rhs}")
            self.stack.append(reg)
        elif isinstance(node, AstPrint):
            self.traverse(node.expr)
            reg = self.stack.pop()
            self.instrs.append(f"print {reg}")

    def generate(self):
        self.traverse(self.root)
        for instr in self.instrs:
            yield instr

#  program = "print 5 + 4 * 3 - 7 - 4 + (3 - 9)\n"
program = "print 2 * ((1 + 1 + 1) / 3)\n"
#  P1 = "5 + 4 * 3\n"
#  P2 = "(5 + 4) * 3\n"
#  P3 = "5 - 3\n"
#  P4 = "(5 / 3) * (4 / 3) + 1\n"

tokens = list(Lexer(program))
parse_tree = Parser(tokens).parse()
node = parse_tree.stmts[0]
gen = CodeGenerator(node)
for instr in gen.generate():
    print(instr)
