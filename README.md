# tinyhttpd — Simple HTTP Server Written in C

A small HTTP daemon written from scratch in C.

The goal of this project is to understand how HTTP servers work internally:
from raw TCP sockets, to request handling, to event-driven architectures.

## Current features

- TCP socket server
- IPv4 and IPv6 support
- HTTP GET handling
- Static file serving
- MIME type detection
- nginx reverse proxy deployment
- systemd service support

---

# TODO

## Server improvements

- Replace `fork()` per request with a worker/event-driven model.
  Forking a new process for every connection is expensive.

- Add graceful shutdown on `SIGTERM` so systemd can stop the daemon cleanly.

- Add a dedicated service user instead of running as `www-data`.

- Add access logging.

- Add `SIGPIPE` handling to prevent a disconnected client from terminating the server.

- Improve HTTP parsing:
  - handle malformed requests
  - validate request methods
  - improve error responses

- Add optional HTTP keep-alive support.

---

# Development roadmap

## Step 1: Complete the current fork-based server

The current implementation is the baseline.

Add:

- proper HTTP parsing
- better error handling
- logging
- graceful shutdown
- improved request handling

Do not throw this version away. It is useful as a reference implementation.

---

## Step 2: Create experimental branches

Example:

```
tinyhttpd/
├── master              # fork-per-connection version
├── poll-version        # poll() based event loop
├── epoll-version       # Linux epoll implementation
└── libuv-version       # libuv based implementation
```

This makes it possible to compare different server architectures.

Reference:

https://eli.thegreenplace.net/2017/concurrent-servers-part-1-introduction/

---

# Running as a systemd daemon

## 1. Create a directory for the daemon

```bash
sudo mkdir -p /opt/tinyhttpd
```

## 2. Copy the binary and static files

```bash
sudo cp ~/c-tiny-http-server/tinyhttpd /opt/tinyhttpd/
sudo cp -r ~/c-tiny-http-server/static /opt/tinyhttpd/
```

## 3. Create the systemd service

Create:

```bash
sudo vim /etc/systemd/system/tinyhttpd.service
```

Add:

```ini
[Unit]
Description=tinyhttpd C HTTP daemon
After=network.target

[Service]
Type=simple

ExecStart=/opt/tinyhttpd/tinyhttpd
WorkingDirectory=/opt/tinyhttpd

Restart=on-failure
RestartSec=5

User=tinyhttpd
Group=tinyhttpd

# Security hardening
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

## 4. Create the service user

```bash
sudo useradd --system --no-create-home --shell /usr/sbin/nologin tinyhttpd
```

## 5. Set ownership

```bash
sudo chown -R tinyhttpd:tinyhttpd /opt/tinyhttpd
```

## 6. Reload systemd

```bash
sudo systemctl daemon-reload
```

## 7. Enable the daemon at boot

```bash
sudo systemctl enable tinyhttpd
```

## 8. Start the daemon

```bash
sudo systemctl start tinyhttpd
```

## 9. Check status

```bash
sudo systemctl status tinyhttpd
```

## 10. Check logs

```bash
sudo journalctl -u tinyhttpd -f
```

## 11. Test

```bash
curl -v https://tiny.shields.nu/
```

---

# Deployment architecture

Current setup:

```
Internet
    |
    v
 nginx
    |
    v
 tinyhttpd
    |
    v
 static files
```

nginx handles:

- TLS termination
- HTTPS certificates
- public networking

tinyhttpd handles:

- TCP connections
- HTTP requests
- file serving
- application logic

---

# Future architecture

The current server uses:

```
one process per connection
```

The long-term goal is:

```
one event loop handling many connections
```

Development path:

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

The final architecture:

```
Client connections
        |
        v
    Event loop
        |
        +-- socket readable
        |
        +-- socket writable
        |
        +-- timers
```

---

# Learning resources

Beejs Network Guide:
https://beej.us/guide/bgnet/html/

Concurrent server development:
https://eli.thegreenplace.net/2017/concurrent-servers-part-1-introduction/

Http RFC9110:
https://datatracker.ietf.org/doc/html/rfc9110
# Testing

See [tests/README.md](tests/README.md) for the test suite.