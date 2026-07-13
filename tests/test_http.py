#!/usr/bin/env python3

import os
import sys
import time
import socket
import subprocess
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor


HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "3490"))

BASE_URL = f"http://{HOST}:{PORT}"

PASSED = 0
FAILED = 0


def passed(name):
    global PASSED
    PASSED += 1
    print(f"[PASS] {name}")


def failed(name, error=""):
    global FAILED
    FAILED += 1
    print(f"[FAIL] {name} {error}")


def http_get(path):
    url = BASE_URL + path

    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            return response.status, response.read()

    except urllib.error.HTTPError as e:
        return e.code, e.read()

    except Exception as e:
        return None, str(e).encode()


def test_root():
    status, body = http_get("/")

    if status == 200 and len(body) > 0:
        passed("GET / returns 200")
    else:
        failed("GET / returns 200", f"got {status}")


def test_missing_file():

    status, _ = http_get("/does-not-exist.html")

    if status == 404:
        passed("Missing file returns 404")
    else:
        failed("Missing file returns 404", f"got {status}")


def test_png():

    status, body = http_get("/rocket.png")

    if status == 200 and body.startswith(b"\x89PNG"):
        passed("PNG served correctly")
    else:
        failed("PNG served correctly")


def test_post():

    request = urllib.request.Request(
        BASE_URL + "/",
        method="POST"
    )

    try:
        urllib.request.urlopen(request)

        failed("POST returns 405", "got 200")

    except urllib.error.HTTPError as e:

        if e.code == 405:
            passed("POST returns 405")
        else:
            failed("POST returns 405", f"got {e.code}")


def test_https():

    try:
        with urllib.request.urlopen(
            "https://tiny.shields.nu/",
            timeout=5
        ) as response:

            if response.status == 200:
                passed("HTTPS reverse proxy works")
            else:
                failed("HTTPS reverse proxy")

    except Exception as e:
        failed("HTTPS reverse proxy works", str(e))


def test_concurrent_requests():

    def request():
        status, _ = http_get("/")
        return status == 200


    with ThreadPoolExecutor(max_workers=25) as executor:

        results = list(
            executor.map(
                lambda _: request(),
                range(100)
            )
        )

    if all(results):
        passed("100 concurrent requests")
    else:
        failed("100 concurrent requests")


def test_malformed_request():

    try:

        with socket.create_connection(
            (HOST, PORT),
            timeout=2
        ) as s:

            s.sendall(
                b"HELLO\r\n\r\n"
            )

            time.sleep(0.2)

        passed("Malformed request handled")

    except Exception as e:
        failed(
            "Malformed request handled",
            str(e)
        )


def get_fd_count():

    pid = subprocess.check_output(
        ["pidof", "tinyhttpd"],
        text=True
    ).strip()

    if not pid:
        return 0

    return len(
        os.listdir(
            f"/proc/{pid}/fd"
        )
    )


def test_fd_leak():

    before = get_fd_count()

    for _ in range(100):
        http_get("/")

    after = get_fd_count()

    difference = after - before

    if difference < 10:
        passed("No obvious file descriptor leak")
    else:
        failed(
            "No obvious file descriptor leak",
            f"fd increase {difference}"
        )


def main():

    print()
    print("tinyhttpd test suite")
    print("--------------------")
    print(f"Target: {BASE_URL}")
    print()

    test_root()
    test_missing_file()
    test_png()
    test_post()
    test_https()
    test_concurrent_requests()
    test_malformed_request()
    test_fd_leak()

    print()
    print("--------------------")
    print(f"Passed: {PASSED}")
    print(f"Failed: {FAILED}")

    if FAILED:
        sys.exit(1)


if __name__ == "__main__":
    main()