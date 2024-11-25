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
        for var_def in self.var_defs:
            instrs.append(var_def.get_instr())
        for stmt in self.stmts:
            instrs += stmt.get_code()
        return instrs

class AstVarDef(Ast):

    def __init__(self, var_id, var_type, literal):
        self.id = var_id
        self.type = var_type
        self.literal = literal

    def __repr__(self):
        return f"AstVarDef(id={self.id}, type={self.type}, literal={self.literal})"

    def get_instr(self):
        return {"dest" : self.id, "type" : self.type, "value" : self.literal, "op" : "const"}

class AstPrint(Ast):

    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"AstPrint({self.expr})"

    def get_code(self):
        global reg
        dest = reg.next()
        inst1 = {"dest" : dest, "type" : self.expr.type}
        if isinstance(self.expr, AstLiteral):
            inst1["op"] = "const"
            inst1["value"] = self.expr.lit
        elif isinstance(self.expr, AstVariable):
            inst1["op"] = "id"
            inst1["args"] = [self.expr.id]
        else:
            raise Exception("Invalid expression for print")
        inst2 = {"op" : "print", "args" : [dest]}
        return [inst1, inst2]

class AstLiteral(Ast):

    def __init__(self, ctype, literal):
        self.type = ctype
        self.lit = literal

    def __repr__(self):
        return f"AstLiteral(type={self.type}, literal={self.lit})"

class AstVariable(Ast):

    def __init__(self, var_type, var_id):
        self.type = var_type
        self.id = var_id

    def __repr__(self):
        return f"AstVariable(type={self.type}, id={self.id})"


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
        self.match(Token.ASSIGN)
        if type_token.value == "int":
            lit_token = self.match(Token.NUM)
        elif type_token.value == "bool":
            lit_token = self.match(Token.BOOL)
        else:
            self.error() # TODO: str token if we want to do that eventually
        self.match("NEWLINE")
        return AstVarDef(id_token.value, type_token.value, lit_token.value)

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
                stmt = AstPrint(expr=self.get_expr())
                self.match(Token.RPAREN)
            else:
                self.error("Only keyword implemented is print") # TODO
        else:
            self.error("Only stmt implemented is AstPrint") # TODO
        self.match("NEWLINE")
        return stmt

    def get_expr(self):
        expr = None
        if self.token() == Token.NUM:
            result = self.match(Token.NUM)
            expr = AstLiteral("int", result.value)
        elif self.token() == Token.ID:
            result = self.match(Token.ID)
            expr = AstVariable("int", result.value) # TODO: need to be look up type in symbol table
        else:
            self.error("only single token expressions implemented so far")
        return expr

if __name__ == "__main__":
    tokens = list(lex_text(sys.stdin.read()))
    parser = Parser(tokens)
    program = parser.get_program()
    func = {"name": "main", "instrs" : program.get_code()}
    prog = {"functions" : [func]}
    json.dump(prog, sys.stdout, indent=4)
