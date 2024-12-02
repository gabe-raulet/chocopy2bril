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

    KEYWORD = TokenPattern.regexp("KEYWORD", r"print")
    TYPE    = TokenPattern.regexp("TYPE", r"int|bool")
    BOOL    = TokenPattern.regexp("BOOL", r"True|False", process=lambda v: {"True" : True, "False" : False}[v])

    ID      = TokenPattern.regexp("ID", r"[a-zA-Z_][a-zA-Z_0-9]*")
    NUM     = TokenPattern.regexp("NUM", r"[0-9]+", process=lambda v: int(v))

    OP_GROUP = [ADD, SUB, MUL, DIV, MOD, AND, OR, EQ, NE, LE, GE, LT, GT, NOT]
    DELIM_GROUP = [LPAREN, RPAREN, COLON, ASSIGN, ARROW, COMMA]
    EXACT_GROUP = [OP_GROUP, DELIM_GROUP]

    OP = TokenPattern.group("OP", OP_GROUP)
    DELIM = TokenPattern.group("DELIM", DELIM_GROUP)

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

        if cls.OP.match(text):
            for op in cls.OP_GROUP:
                if op.match(text):
                    value, text = op.lex_and_split(text)
                    return Token(op.name, value), text

        if cls.DELIM.match(text):
            for delim in cls.DELIM_GROUP:
                if delim.match(text):
                    value, text = delim.lex_and_split(text)
                    return Token(delim.name, value), text

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

class Body(object):

    def __init__(self, table, stmts):
        self.table = table
        self.stmts = stmts
        self.reg = 0

    def next_reg(self):
        reg = f"r{self.reg}"
        self.reg += 1
        return reg

    def get_instrs(self):
        instrs = []
        for name, info in self.table.items():
            instrs.append({"dest" : name, "op" : "const", "value" : info["value"], "type" : info["type"]})
        for stmt in self.stmts:
            instrs += stmt.get_instrs(self)
        return instrs

class Program(Body):

    def __init__(self, table, stmts):
        super().__init__(table, stmts)

    def get_bril(self):
        main = {"name" : "main", "instrs" : self.get_instrs()}
        return {"functions" : [main]}

class Ast(object):
    pass

class AstPrint(Ast):

    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"AstPrint(expr={self.expr})"

    def get_instrs(self, body):
        instrs = self.expr.get_instrs(body)
        dest = instrs[-1]["dest"]
        instrs.append({"op" : "print", "args" : [dest]})
        return instrs

class AstVariable(Ast):

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"AstVariable(name='{self.name}')"

    def get_type(self, table):
        return table[self.name]["type"]

    def get_instrs(self, body):
        dest = body.next_reg()
        return [{"dest" : dest, "op" : "id", "type" : self.get_type(body.table), "args" : [self.name]}]

class AstLiteral(Ast):

    def __init__(self, value, type):
        self.value = value
        self.type = type

    def __repr__(self):
        return f"AstLiteral(value={self.value}, type={self.type})"

    def get_type(self, table):
        return self.type

    def get_instrs(self, body):
        dest = body.next_reg()
        return [{"dest" : dest, "op" : "const", "type" : self.get_type(body.table), "value" : self.value}]

    def evaluate(self):
        return self.value

class AstAssign(Ast):

    def __init__(self, target, expr):
        self.target = target
        self.expr = expr

    def __repr__(self):
        return f"AstAssign(target={self.target}, expr={self.expr})"

    def get_type(self, table):
        return None

    def get_instrs(self, body):
        instrs = self.expr.get_instrs(body)
        args = [instrs[-1]["dest"]]
        type = self.expr.get_type(body.table)
        instrs.append({"dest" : self.target.name, "op" : "id", "type" : type, "args" : args})
        return instrs

class AstBinOp(Ast):

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"AstBinOp(op={self.op}, left={self.left}, right={self.right})"

    @staticmethod
    def traverse(node, body, instrs, stack):
        if isinstance(node, AstBinOp):
            AstBinOp.traverse(node.left, body, instrs, stack)
            AstBinOp.traverse(node.right, body, instrs, stack)
            rhs = stack.pop()
            lhs = stack.pop()
            dest = body.next_reg()
            op = node.op.lower()
            ltype = node.left.get_type(body.table)
            rtype = node.right.get_type(body.table)
            if op == "mod":
                assert ltype == "int" and rtype == "int"
                instrs.append({"dest" : dest, "op" : "div", "type" : "int", "args" : [lhs, rhs]})
                instrs.append({"dest" : dest, "op" : "mul", "type" : "int", "args" : [dest, rhs]})
                instrs.append({"dest" : dest, "op" : "sub", "type" : "int", "args" : [lhs, dest]})
            elif op in {"lt", "gt", "le", "ge"}:
                assert ltype == "int" and rtype == "int"
                instrs.append({"dest" : dest, "op" : op, "type" : "bool", "args" : [lhs, rhs]})
            elif op in {"eq", "ne"}:
                assert ltype == "int" and rtype == "int" # TODO: implement version that works for bools as well
                instrs.append({"dest" : dest, "op" : "eq", "type" : "bool", "args" : [lhs, rhs]})
                if op == "ne":
                    instrs.append({"dest" : dest, "op" : "not", "type" : "bool", "args" : [dest]})
            elif op  in {"or", "and"}:
                assert ltype == "bool" and rtype == "bool"
                instrs.append({"dest" : dest, "op" : op, "type" : "bool", "args" : [lhs, rhs]})
            elif op in {"add", "sub", "mul", "div"}:
                assert ltype == "int" and rtype == "int"
                instrs.append({"dest" : dest, "op" : op, "type" : "int", "args" : [lhs, rhs]})
            else:
                raise Exception("error")
            stack.append(dest)
        else:
            instrs += node.get_instrs(body)
            dest = instrs[-1]["dest"]
            stack.append(dest)

    def get_instrs(self, body):
        instrs, stack = [], []
        AstBinOp.traverse(self, body, instrs, stack)
        return instrs

    def get_type(self, table):
        lhs = self.left.get_type(table)
        rhs = self.right.get_type(table)
        if self.op in {"ADD", "SUB", "MUL", "DIV", "MOD"}:
            assert lhs == "int" and rhs == "int"
            return "int"
        elif self.op in {"LT", "GT", "LE", "GE"}:
            assert lhs == "int" and rhs == "int"
            return "bool"
        elif self.op in {"EQ", "NE"}:
            assert lhs == rhs
            return "bool"
        elif self.op in {"AND", "OR"}:
            assert lhs == "bool" and rhs == "bool"
            return "bool"
        else:
            raise Exception("Type error")


    def evaluate(self):
        lhs = self.left.evaluate()
        rhs = self.right.evaluate()
        if self.op == "ADD": return lhs + rhs
        elif self.op == "SUB": return lhs - rhs
        elif self.op == "MUL": return lhs * rhs
        elif self.op == "DIV": return lhs // rhs
        elif self.op == "MOD": return lhs % rhs
        elif self.op == "AND": return lhs and rhs
        elif self.op == "OR": return lhs or rhs
        elif self.op == "EQ": return lhs == rhs
        elif self.op == "NE": return lhs != rhs
        elif self.op == "LT": return lhs < rhs
        elif self.op == "GT": return lhs > rhs
        elif self.op == "LE": return lhs <= rhs
        elif self.op == "GE": return lhs >= rhs
        else: raise Exception()

class AstUnOp(Ast):

    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def __repr__(self):
        return f"AstUnOp(op={self.op}, expr={self.expr})"

    def get_type(self, table):
        return self.expr.get_type(table)

    def get_instrs(self, body):
        instrs = self.expr.get_instrs(body)
        args = [instrs[-1]["dest"]]
        type = self.get_type(body.table)
        op = self.op.lower()
        dest = body.next_reg()
        if op == "not":
            assert type == "bool"
            instrs.append({"dest" : dest, "op" : "not", "type" : "bool", "args" : args})
        elif op == "usub":
            assert type == "int"
            tmp = body.next_reg()
            instrs.append({"dest" : tmp, "op" : "const", "type" : "int", "value" : -1})
            instrs.append({"dest" : dest, "op" : "mul", "type" : "int", "args" : [tmp, args[0]]})
        else:
            raise Exception("error")
        return instrs

    def evaluate(self):
        if self.op == "NOT": return not self.expr.evaluate()
        elif self.op == "USUB": return -1 * self.expr.evaluate()
        else: raise Exception()

class Parser(object):

    def __init__(self, tokens):
        self.tokens = tokens
        self.size = len(tokens)
        self.pos = 0

    def error(self, msg=""):
        if msg: msg = f": {msg}"
        raise Exception("Syntax error{msg}")

    def token(self, peek_amt=0):
        if self.pos + peek_amt < self.size:
            return self.tokens[self.pos + peek_amt]
        else:
            return None

    def advance(self):
        if self.pos < self.size:
            self.pos += 1

    def match(self, token):
        matchee = self.token()
        if matchee.matches(token): self.advance()
        else: self.error()
        return matchee

    def match_newline(self):
        self.match("NEWLINE")

    def match_indent(self):
        self.match("INDENT")

    def match_dedent(self):
        self.match("DEDENT")

    def not_done(self):
        return self.token() is not None

    def matches_typed_var(self):
        return self.not_done() and self.token().matches(Token.ID) and self.token(1).matches(Token.COLON)

    def get_typed_var(self):
        name = self.match(Token.ID).value
        self.match(Token.COLON)
        type = self.match(Token.TYPE).value
        return name, type

    def get_var_def(self):
        name, type = self.get_typed_var()
        self.match(Token.ASSIGN)
        if type == "int": value = self.match(Token.NUM).value
        elif type == "bool": value = self.match(Token.BOOL).value
        else: self.error(f"unknown type: {type}")
        self.match_newline()
        return name, value, type

    def get_table(self):
        table = {}
        while self.matches_typed_var():
            name, value, type = self.get_var_def()
            table[name] = {"value" : value, "type" : type}
        return table

    def parse(self):
        table = self.get_table()
        stmts = self.get_stmts()
        return Program(table, stmts)

    def matches_keyword(self, word):
        return self.not_done() and self.token().matches(Token.KEYWORD) and self.token().value == word

    def get_print(self):
        self.match(Token.KEYWORD)
        self.match(Token.LPAREN)
        stmt = AstPrint(expr=self.get_expr())
        self.match(Token.RPAREN)
        return stmt

    def matches_assign(self):
        return self.not_done() and self.token().matches(Token.ID) and self.token(1).matches(Token.ASSIGN)

    def get_assign(self):
        target = AstVariable(name=self.match(Token.ID).value)
        self.match(Token.ASSIGN)
        stmt = AstAssign(target=target, expr=self.get_expr())
        return stmt

    def get_stmts(self):
        stmts = []
        while self.token(): stmts.append(self.get_stmt())
        return stmts

    def get_stmt(self):
        stmt = None
        if self.matches_keyword("print"):
            stmt = self.get_print()
        elif self.matches_assign():
            stmt = self.get_assign()
        else:
            self.error()
        self.match_newline()
        return stmt

    def get_atom(self):
        if self.token().matches(Token.LPAREN):
            self.match(Token.LPAREN)
            expr = self.get_expr()
            self.match(Token.RPAREN)
            return expr
        elif self.token().matches(Token.SUB):
            self.advance()
            if self.token().matches(Token.NUM):
                return AstLiteral(value=self.match(Token.NUM).value * -1, type="int")
            else:
                return AstUnOp(op="USUB", expr=self.get_expr())
        elif self.token().matches(Token.NOT):
            self.advance()
            return AstUnOp(op="NOT", expr=self.get_expr())
        elif self.token().matches(Token.NUM):
            return AstLiteral(value=self.match(Token.NUM).value, type="int")
        elif self.token().matches(Token.BOOL):
            return AstLiteral(value=self.match(Token.BOOL).value, type="bool")
        elif self.token().matches(Token.ID):
            return AstVariable(self.match(Token.ID).value)
        else:
            self.error()

    def get_expr(self, min_prec=1):
        lhs = self.get_atom()
        while self.token() and Token.get_precedence(self.token().name) >= min_prec:
            op = self.token().name
            prec = Token.get_precedence(op)
            self.advance()
            lhs = AstBinOp(op=op, left=lhs, right=self.get_expr(prec+1))
        return lhs

if __name__ == "__main__":
    tokens = list(lex_text(sys.stdin.read()))
    parser = Parser(tokens)
    json.dump(parser.parse().get_bril(), sys.stdout, indent=4)

#  text = open("prog6.py").read()
#  tokens = list(lex_text(prog))
#  parser = Parser(tokens)
#  p = parser.parse()
#  json.dump(p.get_bril(), sys.stdout, indent=4)

