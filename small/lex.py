import sys
import re
import json
from norm import normalize_text

patterns = [
        (r"\(", "LPAREN"),
        (r"\)", "RPAREN"),
        (r"\:", "COLON"),
        (r",", "COMMA"),
        (r"\.", "DOT"),
        (r"\+", "ADD"),
        (r"\-", "SUB"),
        (r"\*", "MUL"),
        (r"//", "DIV"),
        (r"%",  "MOD"),
        (r"->", "ARROW"),
        (r"=", "ASSIGN"),
        (r"int|bool", "TYPE"),
        (r"if|elif|else|while", "KEYWORD"),
        (r"print", "PRINT"),
        (r"True|False", "BOOL"),
        (r"[a-zA-Z_][a-zA-Z_0-9]*", "ID"),
        (r"[0-9]+", "NUM")
    ]

json_pats = [{name: pattern} for pattern, name in patterns]
json.dump(json_pats, sys.stdout, indent=4)



#  text = open("test1.py").read()
#  text = normalize_text(text)

#  for line in text.split("\n"):
    #  while line:
        #  line = line.lstrip()
        #  for pattern, name in patterns:
            #  match_obj = re.match(pattern, line)
            #  if match_obj:
                #  value = match_obj.group()
                #  token = (name, value)
                #  print(token)
                #  line = line[match_obj.end():]
                #  break
    #  print(("NEWLINE", None))
