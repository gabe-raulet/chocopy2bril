#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <ctype.h>
#include <math.h>

char *slurp_file(const char *fname, int *count);

int main(int argc, char *argv[])
{
    int size;
    char *text = slurp_file("stdin", &size);

    for (int i = 0; i < size; ++i)
    {
        char c = text[i];
        if (c == '\n') c = '$';

        printf("text[%d] = '%c'\n", i, c);
    }

    free(text);
    return 0;
}

char *slurp_file(const char *fname, int *count)
{
    #define READSIZE 16

    int fd = strcmp(fname, "stdin")? open(fname, O_RDONLY) : STDIN_FILENO;
    assert((fd >= 0));

    int size = 0, nread;
    int cap = 2*READSIZE;

    char *buf = malloc(cap);

    while (1)
    {
        if (size + READSIZE >= cap)
        {
            cap *= 2;
            buf = realloc(buf, cap);
        }

        nread = read(fd, buf + size, READSIZE);
        assert((nread >= 0));

        if (nread == 0)
            break;

        size += nread;
    }

    if (fd != STDIN_FILENO)
        close(fd);

    if (count)
        *count = size;

    return buf;
}
