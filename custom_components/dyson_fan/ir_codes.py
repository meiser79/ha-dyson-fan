"""Dyson Cool infrared command encoding with configurable timings.

`DysonCoolCommand.get_raw_timings()` in `infrared-protocols` follows Dyson's
published Cool-mode timing spec (850us/1660us bit timings). Real remotes can
vary - the defaults below were measured against a physical Dyson AM07
remote (790us/1590us bit timings) - so every timing is user-configurable via
the "IR codes" options step rather than fixed in code.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final, override

from infrared_protocols.commands.dyson import DysonCoolCommand

from .const import (
    CONF_IR_BIT_MARK,
    CONF_IR_FOOTER_MARK,
    CONF_IR_HEADER_MARK,
    CONF_IR_HEADER_SPACE,
    CONF_IR_ONE_SPACE,
    CONF_IR_ZERO_SPACE,
)

DEFAULT_IR_HEADER_MARK: Final = 2440
DEFAULT_IR_HEADER_SPACE: Final = 870
DEFAULT_IR_BIT_MARK: Final = 790
DEFAULT_IR_ZERO_SPACE: Final = 790
DEFAULT_IR_ONE_SPACE: Final = 1590
DEFAULT_IR_FOOTER_MARK: Final = 850

# Timing keyword accepted by ConfigurableDysonCoolCommand -> (options key, default
# in microseconds). The order is the order of the fields in the options form.
IR_TIMINGS: Final[dict[str, tuple[str, int]]] = {
    "header_mark": (CONF_IR_HEADER_MARK, DEFAULT_IR_HEADER_MARK),
    "header_space": (CONF_IR_HEADER_SPACE, DEFAULT_IR_HEADER_SPACE),
    "bit_mark": (CONF_IR_BIT_MARK, DEFAULT_IR_BIT_MARK),
    "zero_space": (CONF_IR_ZERO_SPACE, DEFAULT_IR_ZERO_SPACE),
    "one_space": (CONF_IR_ONE_SPACE, DEFAULT_IR_ONE_SPACE),
    "footer_mark": (CONF_IR_FOOTER_MARK, DEFAULT_IR_FOOTER_MARK),
}


def timings_from_options(options: Mapping[str, Any]) -> dict[str, int]:
    """Return the configured raw timings, falling back to the AM07 defaults."""
    return {
        name: int(options.get(key, default))
        for name, (key, default) in IR_TIMINGS.items()
    }


class ConfigurableDysonCoolCommand(DysonCoolCommand):
    """Dyson Cool infrared command with fully configurable bit timings."""

    def __init__(
        self,
        *,
        code: int,
        header_mark: int = DEFAULT_IR_HEADER_MARK,
        header_space: int = DEFAULT_IR_HEADER_SPACE,
        bit_mark: int = DEFAULT_IR_BIT_MARK,
        zero_space: int = DEFAULT_IR_ZERO_SPACE,
        one_space: int = DEFAULT_IR_ONE_SPACE,
        footer_mark: int = DEFAULT_IR_FOOTER_MARK,
        modulation: int = 38000,
    ) -> None:
        """Initialize the command with an 8-bit code and the given timings."""
        super().__init__(code=code, modulation=modulation)
        self.header_mark = header_mark
        self.header_space = header_space
        self.bit_mark = bit_mark
        self.zero_space = zero_space
        self.one_space = one_space
        self.footer_mark = footer_mark

    @override
    def get_raw_timings(self) -> list[int]:
        """Get raw timings for the command using the configured values."""
        payload = (self._PREAMBLE << 8) | self.code
        timings: list[int] = [self.header_mark, -self.header_space]

        # 15 bits, MSB-first.
        for i in range(14, -1, -1):
            bit = (payload >> i) & 1
            timings.append(self.bit_mark)
            timings.append(-(self.one_space if bit else self.zero_space))

        timings.append(self.footer_mark)

        return timings
