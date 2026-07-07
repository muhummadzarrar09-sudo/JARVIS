from __future__ import annotations

from bravo1.app import build_terminal_channel


def main() -> None:
    channel = build_terminal_channel()
    channel.run()


if __name__ == "__main__":
    main()
