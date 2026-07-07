from __future__ import annotations

from bravo1.channels.terminal import TerminalChannel
from bravo1.config import Settings
from bravo1.core.operator import Operator


def build_terminal_channel() -> TerminalChannel:
    settings = Settings.load()
    operator = Operator(settings)
    return TerminalChannel(operator)
