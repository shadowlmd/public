#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

SCRIPTNAME = Path(__file__).name


def trailing_dot(name: str) -> str:
    return name.rstrip(".") + "."


def main() -> None:
    if len(sys.argv) != 4:  # noqa: PLR2004
        print(f"Usage: python3 {SCRIPTNAME} <DOMAIN> <SERVER> <PORT>")
        sys.exit(1)

    domain = trailing_dot(sys.argv[1])
    server = trailing_dot(sys.argv[2])
    port = sys.argv[3]

    command = ["dig", "+short", "+tls", "-p", port, "a", domain, f"@{server}"]

    result = subprocess.run(command, check=False)  # noqa: S603
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
