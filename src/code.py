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

    def __init__(self, table, stmts, funcs):
        super().__init__(table, stmts)
        self.funcs = funcs

    def get_bril(self):
        main = {"name" : "main", "instrs" : self.get_instrs()}
        return {"functions" : [main]}

class Function(Body):

    def __init__(self, table, stmts, name, sig, ret_type):
        super().__init__(table, stmts)
        self.name = name
        self.sig = sig
        self.ret_type = ret_type

    def __repr__(self):
        return f"Function(name={self.name}, sig={self.sig}, ret_type={self.ret_type})"
