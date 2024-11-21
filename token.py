
class Token(object):

    ADD     = "ADD"     # '+'
    SUB     = "SUB"     # '-'
    MUL     = "MUL"     # '*'
    DIV     = "DIV"     # '/'
    LPAREN  = "LPAREN"  # '('
    RPAREN  = "RPAREN"  # ')'
    ASSIGN  = "ASSIGN"  # '='
    COLON   = "COLON"   # ':'
    COMMA   = "COMMA"   # ','
    NEWLINE = "NEWLINE" # '\n'

    ID  = "ID"  # [a-zA-Z_]
    NUM = "NUM" # [1-9][0-9]*

    PRINT = "PRINT" # 'print'
    RET   = "RET"   # 'return'
    BOOL  = "BOOL"  # 'bool'
    INT   = "INT"   # 'int'
    TRUE  = "TRUE"  # 'True'
    FALSE = "FALSE" # 'False'
    IF    = "IF"    # 'if'
    ELIF  = "ELIF"  # 'elif'
    ELSE  = "ELSE"  # 'else'
    FOR   = "FOR"   # 'for'
    WHILE = "WHILE" # 'while'
    NOT   = "NOT"   # 'not'
    AND   = "AND"   # 'and'
    OR    = "OR"    # 'or'

    EQ = "EQ" # '=='
    NE = "NE" # '!='
    LT = "LT" # '<'
    GT = "GT" # '>'
    LE = "LE" # '<='
    GE = "GE" # '>='

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        v = self.value if self.value != NEWLINE else "\\n"
        return f"Token({self.name}, {self.value})"
