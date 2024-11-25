import sys
import json
from lexer import Token, TokenPattern

if __name__ == "__main__":
    tokens = [Token.from_dict(token) for token in json.load(sys.stdin)]
    for token in tokens: print(token)
