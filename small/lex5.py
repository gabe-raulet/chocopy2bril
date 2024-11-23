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
            (r"//", "DIV"),
            (r"%",  "MOD"),
            (r"->", "ARROW"),
            (r"=",  "ASSIGN"),
            (r"!=", "NE"),
            (r"int|bool", "TYPE"),
            (r"while", "KEYWORD"),
            (r"print", "PRINT"),
            (r"[a-zA-Z_][a-zA-Z_0-9]*", "ID"),
            (r"[1-9]?[0-9]*", "INT"),
            (r"\n", "NEWLINE")
        ]

def logical_lines(text):
    while text:
        cs = re.search(r"([ \t]*#.*\n|[ \t]*\n)", text)
        line, text = text[:cs.start()], text[cs.end():]
        t = text.replace("\n", "$")
        print(f"'{t}'")
        if line: yield line

text = open("test1.py").read()

#  lines = list(logical_lines(text))

#  operators = ["+", "-", "*", "//", "%", "and", "or", "not"]
#  keywords = ["if", "elif", "else", "while"]

#  a = "|".join(map(re.escape, operators))

def normalize_lines(text):
    text = re.sub(r"[ \t]*#.*\n", r"\n", text) # remove comments
    text = re.sub(r"\n\n+", r"\n", text).strip() # remove consecutive newlines
    text = re.sub(r"[ \t]+\n", r"\n", text) # remove line-trailing whitespace
    text = re.sub(r"[ \t]+", r" ", text) # strip extra whitespace
    return text

text2 = normalize_lines(text)
