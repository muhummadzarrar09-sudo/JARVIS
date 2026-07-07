from __future__ import annotations

from bravo1.core.operator import Operator


class TerminalChannel:
    def __init__(self, operator: Operator) -> None:
        self.operator = operator

    def run(self) -> None:
        print("BRAVO-1 terminal scaffold ready. Type `exit` to quit.\n")
        while True:
            try:
                message = input("you> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nbye.")
                return
            if not message:
                continue
            if message.lower() in {"exit", "quit"}:
                print("bye.")
                return
            result = self.operator.handle(message)
            print(f"\nbravo1> {result['reply']}\n")
