import sys
import json
import re

patterns = [
            (r"\(", "LPAREN"),
            (r"\)", "RPAREN"),
            (r"\:", "COLON"),
            (r"\+", "ADD"),
            (r"\-", "SUB"),
            (r"\*", "MUL"),
            (r"\\", "DIV"),
            (r"=",  "ASSIGN"),
            (r"int|bool|str", "TYPE"),
            (r"[a-zA-Z_][a-zA-Z0-9_]*", "ID"),
            (r"0|[1-9][0-9]*", "INTEGER")
        ]

def tokenize(text):
    while text:
        cs = re.search(r"([ \t]*#.*\n|[ \t]*\n)", text)
        line, text = text[:cs.start()].strip(), text[cs.end():]
        while line:
            matched = False
            for pattern, name in patterns:
                m = re.match(pattern, line)
                if m:
                    matched = True
                    value = line[:m.end()]
                    line = line[m.end():]
                    yield (name, value)
            line = line.strip()
        yield ("NEWLINE", r"\n")

text = open("simple.py").read()
l = tokenize(text)
