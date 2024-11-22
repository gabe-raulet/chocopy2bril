import sys
import json

class Token(object):

    ID = "ID"
    OP = "OP"
    DELIM = "DELIM"
    KEYWORD = "KEYWORD"
    INTEGER = "INTEGER"
    INDENT = "INDENT"
    DEDENT = "DEDENT"
    NEWLINE = "NEWLINE"

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def is_symbol(self):
        return self.name in ("OP", "DELIM", "NEWLINE")

    def __repr__(self):
        return f"Token({self.name}, {self.value})"

    def to_dict(self):
        return {"name" : self.name, "value" : self.value}

    @classmethod
    def from_dict(cls, token):
        return cls(token["name"], token["value"])

def logical_lines(f):
    for line in f.readlines():
        index = line.find("#")
        if index != -1: line = line[:index]
        line = line.rstrip()
        if not line: continue
        yield line

f = open("simple.py")
l = logical_lines(f)
for line in logical_lines(f):
    print(f"line='{line}', size={len(line)}")
