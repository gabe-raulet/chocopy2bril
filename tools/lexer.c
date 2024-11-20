#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "stream.h"

int main(int argc, char *argv[])
{
    stream_t stream;
    stream_open("stdin", &stream);

    int c;

    while ((c = stream_get_char(&stream)) >= 0)
    {
        if      (c == '\n') printf("'\\n'\n");
        else if (c == '\t') printf("'\\t'\n");
        else                 printf("'%c'\n", c);
    }

    stream_close(&stream);
    return 0;
}
