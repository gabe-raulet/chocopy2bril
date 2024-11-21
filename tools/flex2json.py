import json
import sys

if __name__ == "__main__":
    tokens = []
    for line in sys.stdin:
        items = line.rstrip().split("\t")
        if len(items) == 1:
            tokens.append({"symbol" : items[0]})
        elif len(items) == 2:
            value = items[1]
            if items[0] in ("INTEGER", "LWSPACE", "LTSPACE"): value = int(value)
            tokens.append({"name" : items[0], "value" : value})
        else:
            raise Exception("error: expect 1 or 2 items per line")
    json.dump(tokens, sys.stdout, indent=4)
