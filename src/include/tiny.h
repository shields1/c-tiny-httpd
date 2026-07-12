#ifndef TINY_H
#define TINY_H
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <sys/wait.h>
#include <signal.h>
#include <errno.h>

#define PORT "3490"
#define BACKLOG 10
#define BUFFER_SIZE 1024
struct mime_map {
    const char *ext;
    const char *type;
};

static const struct mime_map mime_types[] = {
    {".html", "text/html"},
    {".htm", "text/html"},
    {".css", "text/css"},
    {".js", "application/javascript"},
    {".png", "image/png"},
    {".jpg", "image/jpeg"},
    {".jpeg", "image/jpeg"},
    {".gif", "image/gif"},
    {".svg", "image/svg+xml"},
    {".woff", "font/woff"},
    {".woff2", "font/woff2"},
};

int path_to_int(const char *);
const char *parse_path(const char *);
int send_all(int, const char *, size_t);
void send_file(int sock_fd, const char *);
void sigchld_handler(int);
void *get_in_addr(struct sockaddr *);
const char *get_content_type(const char *);

#endif
