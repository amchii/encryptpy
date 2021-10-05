__all__ = ("main",)

import sys


def main():
    from .cli import encryptpy

    sys.exit(encryptpy())


if __name__ == "__main__":
    main()
