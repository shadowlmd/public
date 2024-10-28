#!/usr/bin/env python3

import subprocess
import sys


def trailing_dot(name):
    return name.rstrip('.') + '.'


def main():
    if len(sys.argv) != 4:
        print("Usage: python3 script.py <DOMAIN> <SERVER> <PORT>")
        exit(1)

    domain = trailing_dot(sys.argv[1])
    server = trailing_dot(sys.argv[2])
    port = sys.argv[3]

    command = ["dig", "+short", "+tls", "-p", port, 'a', domain, f"@{server}"]

    result = subprocess.run(command)
    exit(result.returncode)


if __name__ == "__main__":
    main()
