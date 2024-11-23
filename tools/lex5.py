import sys
import json
import re

class Token(object):

    patterns = [
            (r"\(", "LPAREN"),
            (r"\)", "RPAREN"),
            (r"\:", "COLON"),
            (r",",  "COMMA"),
            (r".",  "DOT"),
            (r"\+", "ADD"),
            (r"\-", "SUB"),
            (r"\*", "MUL"),
            (r"\\", "DIV"),
            (r"->", "ARROW"),
            (r"=",  "ASSIGN"),
            (r"[a-zA-Z_][a-zA-Z_0-9]*", "ID"),
            (r"[1-9]?[0-9]*", "INT"),
            (r"int|bool", "TYPE"),
            (r"\n", "NEWLINE")
        ]

class Lexer(object):

    def __init__(self, text):
        self.text = text
