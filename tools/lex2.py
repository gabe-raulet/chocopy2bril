import sys
import json
import re

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

#  def logical_lines(fh):
    #  for line in fh.readlines():
        #  index = line.find("#")
        #  if index != -1: line = line[:index]
        #  line = line.rstrip()
        #  if not line: continue
        #  yield line

stack = [0]
lines = list(open("simple.py"))

blank = re.compile(r"^[ \t]*(#.*\n|\n)")
comment = re.compile(r"#.*\n")
spaces = re.compile(r"^[ \t]+")
identifier = re.compile(r"[a-zA-Z_][a-zA-Z_0-9]*")
keyword = re.compile()

def tokenize_line(line):
    for ident in identifier.findall(line):
        yield ident

for line in lines:
    if not blank.match(line):
        line = comment.split(line)[0].rstrip()
        lspace = spaces.match(line)
        cnt = 0 if not lspace else lspace.end()
        line = line[cnt:]
        for token in tokenize_line(line):
            print(token)

#  for line in lines:
    #  if not blank.match(line):
        #  line = comment.split(line)[0].rstrip()
        #  lspace = spaces.match(line)
        #  cnt = 0 if not lspace else lspace.end()
        #  if cnt > stack[-1]:
            #  print("INDENT")
            #  stack.append(cnt)
        #  while cnt < stack[-1]:
            #  print("DEDENT")
            #  cnt = stack.pop()
