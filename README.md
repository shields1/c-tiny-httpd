# My simple http server written in C

# TODO

* Replace fork() per request with a worker model (forking every connection is expensive).
* Add graceful shutdown on SIGTERM so systemd can stop it cleanly.
* Add a PID/service user that is not www-data.
* Add access logging.
* Add SIGPIPE handling to prevent  one bad client can kill your whole Tiny process

# Add to systemservices

1) Create directory for the server binary
    sudo mkdir -p /opt/tiny
2) Copy the binary and the static files
    sudo cp ~/c-tiny-http-server/tiny /opt/tiny/
    sudo cp -r ~/c-tiny-http-server/static /opt/tiny/
3) Create a systemd service
    sudo vim /etc/systemd/system/tiny.service
and add
        [Unit]
    Description=Tiny C HTTP Server
    After=network.target

    [Service]
    Type=simple

    ExecStart=/opt/tiny/tiny

    WorkingDirectory=/opt/tiny

    Restart=on-failure
    RestartSec=5

    User=www-data
    Group=www-data

   # Security hardening

    NoNewPrivileges=true
    PrivateTmp=true

    [Install]
    WantedBy=multi-user.target
4) Set ownership
    sudo chown -R www-data:www-data /opt/tiny
5) Tell systemd to reload
    sudo systemctl daemon-reload
6) Enable at boot
    sudo systemctl enable tiny
7) Start server
    sudo systemctl start tiny
8) Check status
    sudo systemctl status tiny
9) Check logs
    sudo journalctl -u tiny -f
10) Test
    curl -v <https://tiny.shields.nu/>
