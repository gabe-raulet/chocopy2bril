import re
import sys
import json
from lexer import lex_text
from parser import Parser
#  from lexer import Token, TokenPattern, lex_text
#  from code import Body, Program, Function
#  from myast import *

if __name__ == "__main__":
    tokens = list(lex_text(sys.stdin.read()))
    parser = Parser(tokens)
    json.dump(parser.parse().get_bril(), sys.stdout, indent=4)

#  text = open("prog9.py").read()
#  tokens = list(lex_text(text))
#  parser = Parser(tokens)
#  prog = parser.parse()
