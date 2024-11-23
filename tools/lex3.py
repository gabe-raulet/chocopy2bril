import sys
import json
import re

#  patterns = [
        #  (r"([:(),.]|->)", "SEP"),
        #  (r"([+\-]|//|%|<|>|<=|>=|!=|==|=)", "OP"),
        #  (r"(bool|int|str)", "TYPE"),
        #  (r"(False|True)", "BOOL"),
        #  (r"(and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|raise|return|try|while|with|yield|print)", "KEYWORD"),
        #  (r"(0|[1-9][0-9]*)", "INT"),
        #  (r"[a-zA-Z_]([a-zA-Z_]|[0-9])*", "ID")
        #  ]

patterns = [
            (
                r"([:(),.]|->)",
                lambda x: {":": "COLON", "(": "LPAREN", ")": "RPAREN", ""}[x]
            )
        ]

text = open("prime.py").read()

def logical_lines(text):
    while text:
        cs = re.search(r"([ \t]*#.*\n|[ \t]*\n)", text)
        line, text = text[:cs.start()], text[cs.end():]
        if line: yield line

def tokenize_line(line):
    lspace = re.match(r"[ \t]+", line)
    if lspace:
        n = lspace.end()
        yield ("LSPACE", n)
        line = line[n:]
    yield line

def tokenize(text):
    for line in logical_lines(text):
        while line:
            matched = False
            for pattern, name in patterns:
                line = line.strip()
                m = re.match(pattern, line)
                if m:
                    matched = True
                    value = line[:m.end()]
                    line = line[m.end():]
                    yield (name, value)
                    break
        yield ("NEWLINE", "\\n")

l = tokenize(text)
