import sys
import re

def normalize_text(text):
    text = re.sub(r"[ \t]*#.*\n", r"\n", text) # remove comments
    text = re.sub(r"\n\n+", r"\n", text).strip() # remove consecutive newlines
    text = re.sub(r"[ \t]+\n", r"\n", text) # remove line-trailing whitespace
    text = re.sub(r"[ \t]+", r" ", text) # strip extra whitespace
    return text

if __name__ == "__main__":
    sys.stdout.write(normalize_text(sys.stdin.read()))
    sys.stdout.flush()
