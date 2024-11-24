import sys
import json
from lex import Token

if __name__ == "__main__":
    tokens = [Token.from_dict(token) for token in json.load(sys.stdin)]
