"""Tests for power decoding and stable feedback."""

from __future__ import annotations

import pytest

from custom_components.dyson_fan.const import (
    CONF_POWER_OSCILLATION_DELTA,
    DEFAULT_POWER_SIGNATURES,
    power_signature_key,
)
from custom_components.dyson_fan.models import FanState
from custom_components.dyson_fan.power import (
    InvalidPowerReading,
    PowerDecoder,
    PowerSignatureTable,
    StablePowerTracker,
    power_to_watts,
)


@pytest.fixture
def decoder() -> PowerDecoder:
    """Return a decoder using the built-in Dyson table."""
    return PowerDecoder(PowerSignatureTable.from_options({}))


def test_exact_signatures(decoder: PowerDecoder) -> None:
    """Every built-in signature maps back to its physical state."""
    table = PowerSignatureTable.from_options({})
    for (speed, oscillating), watts in table.speeds.items():
        assert decoder.decode(watts).state == FanState(True, speed, oscillating)


def test_legacy_oscillation_values_become_one_median_increment() -> None:
    """Existing 21-state tables migrate without favoring one noisy speed."""
    options: dict[str, float] = {}
    for (speed, oscillating), watts in DEFAULT_POWER_SIGNATURES.items():
        options[power_signature_key(speed, oscillating)] = watts

    table = PowerSignatureTable.from_options(options)

    assert table.oscillation_delta == 2.9
    assert table.as_options()[CONF_POWER_OSCILLATION_DELTA] == 2.9
    assert all(
        table.speeds[(speed, True)] - table.speeds[(speed, False)] == pytest.approx(2.9)
        for speed in range(1, 11)
    )


def test_off_and_negative_meter_direction(decoder: PowerDecoder) -> None:
    """Off decodes correctly and reversed meters are treated as absolute power."""
    assert decoder.decode(1.2).state == FanState(False, None, False)
    assert decoder.decode(-18.2).state == FanState(True, 5, False)


@pytest.mark.parametrize("unit", ["W", "kW", None, "", "   "])
@pytest.mark.parametrize("sign", [1, -1])
def test_units_and_signs_preserve_all_power_states(
    decoder: PowerDecoder, unit: str | None, sign: int
) -> None:
    """Every off/speed/oscillation signature is equivalent in either direction."""
    divisor = 1000 if unit == "kW" else 1
    table = decoder.table
    for watts in [table.off, *table.speeds.values()]:
        normalized = power_to_watts(sign * watts / divisor, unit)
        decoded = decoder.decode(normalized)
        assert decoded.state == decoder.decode(watts).state
        assert decoded.watts == pytest.approx(watts)
    with pytest.raises(InvalidPowerReading, match="safety limit"):
        decoder.decode(power_to_watts(sign * 100.1 / divisor, unit))


@pytest.mark.parametrize("value", ["unknown", None, float("nan"), 100.1, -500])
def test_invalid_or_unsafe_power(decoder: PowerDecoder, value: object) -> None:
    """Non-numeric and greater-than-100 W readings are rejected."""
    with pytest.raises(InvalidPowerReading):
        decoder.decode(value)


def test_stability_uses_reports_not_watt_equality(decoder: PowerDecoder) -> None:
    """Slightly different wattages can confirm the same decoded physical state."""
    tracker = StablePowerTracker(3)
    assert tracker.add(decoder.decode(18.0), 0.0) is None
    assert tracker.add(decoder.decode(18.2), 1.0) is None
    stable = tracker.add(decoder.decode(18.4), 2.0)
    assert stable is not None
    assert stable.decoded.state == FanState(True, 5, False)
    assert tracker.add(decoder.decode(18.3), 3.0) is None


def test_stability_resets_when_decoded_state_changes(decoder: PowerDecoder) -> None:
    """A different decoded state starts a new consecutive report run."""
    tracker = StablePowerTracker(2)
    assert tracker.add(decoder.decode(18.2), 0.0) is None
    assert tracker.add(decoder.decode(22.8), 1.0) is None
    stable = tracker.add(decoder.decode(22.9), 2.0)
    assert stable is not None
    assert stable.decoded.state.speed == 6


def test_steady_quiet_sensor_is_accepted_after_the_timeout(
    decoder: PowerDecoder,
) -> None:
    """A report-on-change sensor never sends the required number of reports."""
    tracker = StablePowerTracker(3)
    assert tracker.add(decoder.decode(18.2), 100.0) is None
    assert tracker.check_timeout(120.0, 45) is None
    stable = tracker.check_timeout(146.0, 45)
    assert stable is not None
    assert stable.decoded.state == FanState(True, 5, False)
    assert tracker.check_timeout(200.0, 45) is None


def test_timeout_restarts_when_the_decoded_state_changes(
    decoder: PowerDecoder,
) -> None:
    """The hold time is measured from the first report of the current state."""
    tracker = StablePowerTracker(3)
    assert tracker.add(decoder.decode(18.2), 0.0) is None
    assert tracker.add(decoder.decode(22.8), 40.0) is None
    assert tracker.check_timeout(50.0, 45) is None
    assert tracker.check_timeout(86.0, 45) is not None
