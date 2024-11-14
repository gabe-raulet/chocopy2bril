import unittest
from interp import Interpreter

class TestInterpreter(unittest.TestCase):

    def test_binary_ops(self):
        for x in range(15):
            for y in range(1, 15):
                self.assertEqual(x + y, Interpreter.interpret(f"{x} + {y}"))
                self.assertEqual(x * y, Interpreter.interpret(f"{x} * {y}"))
                for z in range(1, 15):
                    self.assertEqual(x + y + z, Interpreter.interpret(f"{x} + {y} + {z}"))
                    self.assertEqual(x * y * z, Interpreter.interpret(f"{x} * {y} * {z}"))
                    self.assertEqual(x + y * z, Interpreter.interpret(f"{x} + {y} * {z}"))
                    self.assertEqual(x * y + z, Interpreter.interpret(f"{x} * {y} + {z}"))
                    self.assertEqual((x + y) * z, Interpreter.interpret(f"({x} + {y}) * {z}"))
                    self.assertEqual(x + (y * z), Interpreter.interpret(f"{x} + ({y} * {z})"))
                    for w in range(1, 15):
                        self.assertEqual((x + y) * (w + z), Interpreter.interpret(f"({x} + {y}) * ({w} + {z})"))
                        self.assertEqual((x + y) + (w * z), Interpreter.interpret(f"({x} + {y}) + ({w} * {z})"))
                        self.assertEqual((x * y) + (w + z), Interpreter.interpret(f"({x} * {y}) + ({w} + {z})"))
                        self.assertEqual(((x + y + w) * z), Interpreter.interpret(f"({x} + {y} + {w}) * {z}"))

if __name__ == "__main__":
    unittest.main()
