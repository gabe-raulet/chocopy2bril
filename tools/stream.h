#ifndef STREAM_H_
#define STREAM_H_

#include <stdio.h>
#include <assert.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <math.h>

#define BUFLEN (16)

typedef struct
{
    int fd, start, end, is_eof;
    char *buf;
} stream_t;

int stream_open(const char *fname, stream_t *stream);
int stream_close(stream_t *stream);
int stream_get_char(stream_t *stream);
int stream_peek_char(stream_t *stream);
int stream_buffer_new_chars(stream_t *stream);

int stream_open(const char *fname, stream_t *stream)
{
    if (fname == NULL || stream == NULL)
        return -1;

    stream->fd = strcmp(fname, "stdin")? open(fname, O_RDONLY) : STDIN_FILENO;
    if (stream->fd < 0) return -1;

    stream->start = stream->end = stream->is_eof = 0;
    stream->buf = malloc(BUFLEN);

    return 0;
}

int stream_close(stream_t *stream)
{
    if (stream == NULL)
        return -1;

    if (stream->fd != STDIN_FILENO)
        close(stream->fd);

    free(stream->buf);
    memset(stream, 0, sizeof(stream_t));

    return 0;
}

int stream_buffer_new_chars(stream_t *stream)
{
    if (stream->is_eof)
        return -1;

    if (stream->start >= stream->end)
    {
        stream->start = 0;
        stream->end = read(stream->fd, stream->buf, BUFLEN);
        assert((stream->end >= 0));

        if (stream->end == 0)
        {
            stream->is_eof = 1;
            return -1;
        }
    }

    return 0;
}

int stream_get_char(stream_t *stream)
{
    if (stream->is_eof)
        return -1;

    stream_buffer_new_chars(stream);

    return stream->buf[stream->start++];
}

int stream_peek_char(stream_t *stream)
{
    if (stream->is_eof)
        return -1;

    stream_buffer_new_chars(stream);

    return stream->buf[stream->start];
}

#endif
