# tinyhttpd Tests

This directory contains tests for tinyhttpd.

The goal is to verify:

- HTTP correctness
- error handling
- stability under bad clients
- file serving
- connection handling
- resource usage

The tests are intended to be run against a running tinyhttpd instance.

---

# Requirements

Install test tools:

```bash
sudo apt install curl apache2-utils valgrind netcat-openbsd
```

---

# Basic HTTP Tests

## Test root page

```bash
curl -v http://127.0.0.1:3490/
```

Expected:

```
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: ...
Connection: close
Server: Tiny
```

---

## Test HTTPS through nginx

```bash
curl -v https://tiny.shields.nu/
```

This verifies:

- TLS termination
- nginx reverse proxy
- tinyhttpd response

---

## Test missing files

```bash
curl -v http://127.0.0.1:3490/missing.html
```

Expected:

```
HTTP/1.1 404 Not Found
```

---

## Test static binary files

Example:

```bash
curl -v http://127.0.0.1:3490/rocket.png -o /tmp/rocket.png
```

Verify:

```bash
file /tmp/rocket.png
```

Expected:

```
PNG image data
```

---

# HTTP Method Tests

tinyhttpd currently supports GET only.

## Test unsupported method

```bash
curl -v -X POST http://127.0.0.1:3490/
```

Expected:

```
HTTP/1.1 405 Method Not Allowed
```

---

# Malformed Request Tests

Use netcat:

```bash
nc 127.0.0.1 3490
```

Send invalid requests:

```
HELLO
```

or:

```
GET
```

or:

```
GET / HTTP/1.1
```

The server should:

- not crash
- close the connection
- continue accepting new clients

---

# Connection Tests

## SIGPIPE test

A disconnected client should not terminate tinyhttpd.

Example:

```bash
curl http://127.0.0.1:3490/ &
kill $!
```

Verify:

```bash
systemctl status tinyhttpd
```

The daemon should still be running.

---

# Load Testing

Install ApacheBench:

```bash
sudo apt install apache2-utils
```

Run:

```bash
ab -n 1000 -c 50 http://127.0.0.1:3490/
```

Meaning:

```
-n 1000  total requests
-c 50    concurrent clients
```

Verify:

- no crashes
- no stuck connections
- no excessive memory usage

---

# Slow Client Test

Open a connection:

```bash
nc 127.0.0.1 3490
```

Send:

```
GET /
```

Then wait.

The server should remain responsive.

This test is important because blocking clients can expose design problems.

---

# File Descriptor Leak Test

Run:

```bash
for i in {1..100}; do
    curl -s http://127.0.0.1:3490/ > /dev/null
done
```

Check open file descriptors:

```bash
ls /proc/$(pidof tinyhttpd)/fd | wc -l
```

Repeat the test several times.

The number should remain stable.

---

# Memory Testing

Run tinyhttpd under Valgrind:

```bash
valgrind \
--leak-check=full \
./tinyhttpd
```

Make requests:

```bash
curl http://127.0.0.1:3490/
```

Check for:

```
definitely lost: 0 bytes
```

---

# Automated Tests

The shell test suite:

```
test_http.sh
```

can be run with:

```bash
chmod +x test_http.sh
./test_http.sh
```

The script should exit with:

```
0
```

when all tests pass.

---

# Future Tests

Planned additions:

- HTTP parser fuzzing
- keep-alive tests
- concurrent connection tests
- epoll event loop tests
- HTTP header validation
- invalid URI handling
- large file transfers
- graceful shutdown tests

---

# Development Goal

These tests are intended to follow the evolution of tinyhttpd:

```
fork()
   |
   v
poll()
   |
   v
epoll()
   |
   v
libuv
```

Each new architecture should pass the same test suite.