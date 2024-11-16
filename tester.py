import unittest
from interp import interpret

class TestInterpreter(unittest.TestCase):

    def test_simple(self):
        for x in range(15):
            for y in range(15):
                self.assertEqual(x + y, interpret(f"{x} + {y}"))
                self.assertEqual(x * y, interpret(f"{x} * {y}"))

    def test_compound(self):
        for x in range(15):
            for y in range(15):
                for z in range(15):
                    self.assertEqual(x + y + z, interpret(f"{x} + {y} + {z}"))
                    self.assertEqual(x * y * z, interpret(f"{x} * {y} * {z}"))

    def test_precedence(self):
        for x in range(15):
            for y in range(15):
                for z in range(15):
                    self.assertEqual(x + y * z, interpret(f"{x} + {y} * {z}"))
                    self.assertEqual(x * y + z, interpret(f"{x} * {y} + {z}"))

    def test_association(self):
        for x in range(15):
            for y in range(15):
                for z in range(15):
                    self.assertEqual((x + y) * z, interpret(f"({x} + {y}) * {z}"))
                    self.assertEqual(x * (y + z), interpret(f"{x} * ({y} + {z})"))
                    self.assertEqual((x * y) + z, interpret(f"({x} * {y}) + {z}"))
                    self.assertEqual(x + (y * z), interpret(f"{x} + ({y} * {z})"))

if __name__ == "__main__":
    unittest.main()
