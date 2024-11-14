class Interpreter(object):

    def __init__(self, program):
        self.program = program

    def evaluate(self):
        return eval(self.program)

    @classmethod
    def interpret(cls, program):
        return cls(program).evaluate()
