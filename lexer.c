#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "stream.h"

int main(int argc, char *argv[])
{
    stream_t stream;
    stream_open("ex1.py", &stream);

    int c;

    while ((c = stream_get_char(&stream)) >= 0)
        printf("'%c'\n", c);

    stream_close(&stream);
    return 0;
}
