#ifndef LEXER_H_
#define LEXER_H_

#include "stream.h"
#include <ctype.h>

#define NEWLINE 10 // '\n'
#define MOD     37 // '%'
#define LPAREN  40 // '('
#define RPAREN  41 // ')'
#define MUL     42 // '*'
#define ADD     43 // '+'
#define COMMA   44 // ','
#define SUB     45 // '-'
#define DIV     47 // '/'
#define COLON   58 // ':'
#define ASSIGN  61 // '='

#define ID  256 // [a-zA-Z_]
#define NUM 257 // (0 | [1-9][0-9]*)

#define PRINT 258 // "print"
#define RET   259 // "return"
#define BOOL  260 // "bool"
#define INT   261 // "int"
#define TRUE  262 // "True"
#define FALSE 263 // "False"
#define IF    264 // "if"
#define ELIF  265 // "elif"
#define ELSE  266 // "else"
#define FOR   267 // "for"
#define WHILE 268 // "while"
#define NOT   269 // "not"
#define AND   270 // "and"
#define OR    271 // "or"

#define EQ 272 // '=='
#define NE 273 // '!='
#define LT 274 // '<'
#define GT 275 // '>'
#define LE 276 // '<='
#define GE 277 // '>='

typedef struct
{
    int name;

    union
    {
        int num;
        char str[256];
    } value;

} token_t;

typedef struct
{
    token_t token;
    stream_t *stream;
    int cur;
} lexer_t;

int lexer_init(lexer_t *lexer, stream_t *stream)
{
    if (lexer == NULL || stream == NULL || stream->is_eof)
        return -1;

    lexer->stream = stream;
    lexer->cur = stream_peek_char(stream);

    return 0;
}

int lexer_advance(lexer_t *lexer)
{
    int ch = stream_peek_char(lexer->stream);
}

#endif
