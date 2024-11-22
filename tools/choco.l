LETTER  [a-zA-Z_]
DIGIT   [0-9]
INTEGER (0|[1-9]{DIGIT}*)
ID      {LETTER}({LETTER}|{DIGIT})*
OP      [+\0*%<>]|is|"//"|"!="|"<="|">="|"=="|"="
SEP     [(),\[\].:]|"->"
KEYWORD False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|raise|return|try|while|with|yield|print|int|bool|str
STRING  \"([^\\\"]|\\.)*\"
SPACE   [ \t]*
LWSPACE ^[ ]+
LTSPACE ^[\t]+
COMMENT #.*\n
BLANK   ^[ \t]*({COMMENT}|\n)

%%

{BLANK} ;
{LWSPACE} printf("LWSPACE\t%d\n", (int)yyleng);
{LTSPACE} printf("LTSPACE\t%d\n", (int)yyleng);
{SPACE} ;
{COMMENT} printf("NEWLINE\n");
{STRING} printf("error: do not currently accept string literals: %s\n", yytext);
{KEYWORD} printf("KEYWORD\t%s\n", yytext);
{ID} printf("ID\t%s\n", yytext);
{INTEGER} printf("INTEGER\t%s\n", yytext);
({OP}|{SEP}) printf("%s\n", yytext);
\n printf("NEWLINE\n");
. printf("error: unrecognized character: %s\n", yytext);
