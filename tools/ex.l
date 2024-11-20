LETTER [a-zA-Z_]
DIGIT [0-9]
ALPHA [a-zA-Z0-9_]
SPACE [ \t]*
BSPACE ^[ \t]+
ID {LETTER}({LETTER}|{DIGIT})*
INTEGER {DIGIT}+
STRING \"([^\\\"]|\\.)*\"
BINOP [+\-*%<>]|is|"//"|"!="|"<="|">="|"=="
TERM "("|")"|"="|","|"["|"]"|"."|"->"|":"
KEYWORD False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|raise|return|try|while|with|yield|print
TYPE int|bool|str
COMMENT ^{SPACE}#.*\n

%%

{BSPACE}   printf("BSPACE\t$%s$\n", yytext);

{COMMENT} ;

{SPACE} ;

{STRING}    printf("STRING\t%s\n", yytext);

{TYPE}      printf("TYPE\t%s\n", yytext);

{KEYWORD}   printf("KEYWORD\t%s\n", yytext);

{ID}        printf("ID\t%s\n", yytext);

{INTEGER}   printf("INTEGER\t%s\n", yytext);

{BINOP}     printf("BINOP\t%s\n", yytext);

{TERM}      printf("TERM\t%s\n", yytext);

\n          printf("NEWLINE\n");

.           printf("error: unrecognized character: %s\n", yytext);
