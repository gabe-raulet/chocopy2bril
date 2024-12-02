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

class AstReturn(Ast):

    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"AstReturn(expr={self.expr})"

    def get_type(self, table):
        return None

class AstCall(Ast):

    def __init__(self, name, params):
        self.name = name
        self.params = params

    def __repr__(self):
        return f"AstCall(name={self.name}, params={self.params})"

    def get_type(self, table):
        return None

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
