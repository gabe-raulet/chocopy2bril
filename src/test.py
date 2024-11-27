import sys
import json
from lexer import Token, lex_text
from parse import *

def read_text(fname):
    return open(fname).read()

def read_tokens(text):
    return list(lex_text(text))

tokens = read_tokens(read_text("t6.py"))
parser = Parser(tokens)
prog = parser.parse()

