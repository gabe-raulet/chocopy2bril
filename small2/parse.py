import sys
import json
from lexer import Token, TokenPattern, lex_text

class Register(object):

    def __init__(self):
        self.cur = 0

    def reset(self):
        self.cur = 0

    def next(self):
        name = f"_v{self.cur}"
        self.cur += 1
        return name

reg = Register()

class Ast(object):
    pass

class AstProgram(Ast):

    def __init__(self, var_defs, stmts):
        self.var_defs = var_defs
        self.stmts = stmts

    def __repr__(self):
        return f"var_defs={self.var_defs}\nstmts={self.stmts}"

    def get_code(self):
        instrs = []
        for var_def in self.var_defs: instrs.append(var_def.get_instr())
        for stmt in self.stmts: instrs += stmt.get_code()
        return instrs

class AstVarDef(Ast):

    def __init__(self, name, lit):
        self.id = name
        self.lit = lit

    def __repr__(self):
        return f"AstVarDef(id={self.id}, lit={self.lit})"

    def get_instr(self):
        return {"dest" : self.id, "type" : "int", "value" : self.lit, "op" : "const"}

class AstPrint(Ast):

    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"AstPrint({self.expr})"

    def get_code(self):
        global reg
        dest = reg.next()
        def_inst = self.expr.get_tmp_assign_instr(dest)
        print_inst = {"op" : "print", "args" : [dest]}
        return [def_inst, print_inst]

class AstLiteral(Ast):

    def __init__(self, lit):
        self.lit = lit

    def __repr__(self):
        return f"AstLiteral({self.lit})"

    def get_tmp_assign_instr(self, dest):
        return {"dest" : dest, "type" : "int", "op" : "const", "value" : self.lit}

class AstVariable(Ast):

    def __init__(self, name):
        self.id = name

    def __repr__(self):
        return f"AstVariable({self.id})"

    def get_tmp_assign_instr(self, dest):
        return {"dest" : dest, "type" : "int", "op" : "id", "args" : [self.id]}

class AstBinOp(Ast):

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"AstBinOp(op={self.op}, left={self.left}, right={self.right})"

class AstAssign(Ast):

    def __init__(self, target, expr):
        self.target = target
        self.expr = expr

    def __repr__(self):
        return f"AstAssign(target={self.target}, expr={self.expr})"

    def get_code(self):
        global reg
        dest = reg.next()
        def_inst = self.expr.get_tmp_assign_instr(dest)
        assign_inst = {"dest" : self.target, "type": "int", "op" : "id", "args" : [dest]}
        return [def_inst, assign_inst]

class Parser(object):

    def __init__(self, tokens):
        self.tokens = tokens
        self.size = len(tokens)
        self.pos = 0

    def error(self, msg=None):
        raise Exception("Syntax error" if not msg else f"Syntax error: {msg}")

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
        if matchee == token: self.advance()
        else: self.error()
        return matchee

    def match_newline(self):
        self.match("NEWLINE")

    def get_program(self):
        var_defs = self.get_var_defs()
        stmts = self.get_stmts()
        return AstProgram(var_defs, stmts)

    def get_var_defs(self):
        var_defs = []
        while self.token() == Token.ID and self.token(1) == Token.COLON:
            var_defs.append(self.get_var_def())
        return var_defs

    def get_var_def(self):
        id_token = self.match(Token.ID)
        self.match(Token.COLON)
        type_token = self.match(Token.TYPE)
        assert type_token.value == "int" # TODO temporary
        self.match(Token.ASSIGN)
        lit_token = self.match(Token.NUM)
        self.match_newline()
        return AstVarDef(id_token.value, lit_token.value)

    def get_stmts(self):
        stmts = []
        while self.token(): stmts.append(self.get_stmt())
        return stmts

    def get_stmt(self):
        stmt = None
        if self.token() == Token.KEYWORD:
            if self.token().lexeme() == "print":
                self.match(Token.KEYWORD)
                self.match(Token.LPAREN)
                stmt = AstPrint(self.get_expr())
                self.match(Token.RPAREN)
            else:
                self.error("Only keyword implemented is print, currently") # TODO
        elif self.token() == Token.ID and self.token(1) == Token.ASSIGN:
            target_token = self.match(Token.ID)
            self.match(Token.ASSIGN)
            stmt = AstAssign(target_token.value, self.get_expr())
        else: self.error()
        self.match_newline()
        return stmt

    def get_expr(self):
        expr = self.get_term()
        while self.token() == Token.ADD or self.token() == Token.SUB:
            op = self.token().name
            self.match(op)
            expr = AstBinOp(op=op, left=expr, right=self.get_term())
        return expr

    def get_term(self):
        term = self.get_factor()
        while self.token() == Token.MUL or self.token() == Token.DIV or self.token() == Token.MOD:
            op = self.token().name
            self.match(op)
            term = AstBinOp(op=op, left=term, right=self.get_factor())
        return term

    def get_factor(self):
        if self.token() == Token.LPAREN:
            self.match(Token.LPAREN)
            factor = self.get_expr()
            self.match(Token.RPAREN)
            return factor
        elif self.token() == Token.NUM:
            return AstLiteral(self.match(Token.NUM).value)
        elif self.token() == Token.ID:
            return AstVariable(self.match(Token.ID).value)
        else:
            self.error()

def read_text(fname):
    return open(fname).read()

if __name__ == "__main__":
    tokens = [Token.from_dict(token) for token in json.load(sys.stdin)]
    parser = Parser(tokens)
    program = parser.get_program()
    func = {"name" : "main", "instrs" : program.get_code()}
    prog = {"functions" : [func]}
    json.dump(prog, sys.stdout, indent=4)

#  tokens = list(lex_text(read_text("t4.py")))
