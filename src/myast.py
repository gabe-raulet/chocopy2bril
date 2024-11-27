import re

class Ast(object):
    pass

class AstPrint(Ast):

    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"AstPrint({self.expr})"

    def get_instrs(self, func):
        instrs, dest = self.expr.get_instrs(func)
        instrs.append({"op" : "print", "args" : [dest]})
        return instrs

class AstAssign(Ast):

    def __init__(self, target, expr):
        self.target = target
        self.expr = expr

    def __repr__(self):
        return f"AstAssign(target={self.target}, expr={self.expr})"

    def get_instrs(self, func):
        instrs, dest = self.expr.get_instrs(func)
        instrs.append({"dest" : self.target.name, "type" : self.target.type, "op" : "id", "args" : [dest]})
        return instrs

class AstLiteral(Ast):

    def __init__(self, lit):
        self.lit = lit
        self.type = "int"

    def __repr__(self):
        return f"AstLiteral(lit={self.lit}, type={self.type})"

    def get_instrs(self, func):
        dest = func.next_reg()
        return [{"dest" : dest, "type" : self.type, "op" : "const", "value" : self.lit}], dest

class AstVariable(Ast):

    def __init__(self, name):
        self.name = name
        self.type = "int"

    def __repr__(self):
        return f"AstVariable(name={self.name}, type={self.type})"

    def get_instrs(self, func):
        dest = func.next_reg()
        return [{"dest" : dest, "type" : self.type, "op" : "id", "args" : [self.name]}], dest

class AstVarDef(Ast):

    def __init__(self, var, lit):
        m_obj = re.match(r"r[0-9]+", var.name)
        if m_obj and m_obj.group() == var.name: raise Exception("Can't use register names as variables")
        assert var.type == lit.type
        self.var = var
        self.lit = lit

    def __repr__(self):
        return f"AstVarDef({self.var}, {self.lit})"

    def get_instr(self):
        return {"dest" : self.var.name, "type" : self.var.type, "value" : self.lit.lit, "op" : "const"}

class AstBinOp(Ast):

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"AstBinOp(op={self.op}, left={self.left}, right={self.right})"

    @staticmethod
    def value_instr(dest, op, lhs, rhs, func):
        op = op.lower()
        if op == "mod":
            instrs = []
            instrs.append({"dest" : dest, "op" : "div", "type" : "int", "args" : [lhs, rhs]})
            instrs.append({"dest" : dest, "op" : "mul", "type" : "int", "args" : [dest, rhs]})
            instrs.append({"dest" : dest, "op" : "sub", "type" : "int", "args" : [lhs, dest]})
            return instrs
        else:
            return [{"dest" : dest, "op" : op, "type" : "int", "args" : [lhs, rhs]}]

    @staticmethod
    def traverse(node, func, instrs, stack):
        if isinstance(node, AstBinOp):
            AstBinOp.traverse(node.left, func, instrs, stack)
            AstBinOp.traverse(node.right, func, instrs, stack)
            rhs = stack.pop()
            lhs = stack.pop()
            dest = func.next_reg()
            instrs += AstBinOp.value_instr(dest, node.op, lhs, rhs, func)
            stack.append(dest)
        else:
            insts, dest = node.get_instrs(func)
            instrs += insts
            stack.append(dest)

    def get_instrs(self, func):
        instrs = []
        stack = []
        AstBinOp.traverse(self, func, instrs, stack)
        dest = stack.pop()
        return instrs, dest
