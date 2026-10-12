"""Downloadable diagnostics for Dyson Fan."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from . import DysonFanConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: DysonFanConfigEntry
) -> dict[str, Any]:
    """Return non-sensitive configuration and runtime diagnostics."""
    return {
        "entry": {
            "title": entry.title,
            "options": dict(entry.options),
            "power_sensor": entry.runtime_data.controller.power_sensor,
            "infrared_emitter_entity_id": (
                entry.runtime_data.controller.infrared_emitter_entity_id
            ),
            "ir_timings": entry.runtime_data.controller.ir_timings,
            "feedback_burst_configured": (
                entry.runtime_data.controller.feedback_burst_configured
            ),
            "configured_codes": sorted(
                key for key in entry.data if key.endswith("_code")
            ),
        },
        "controller": entry.runtime_data.controller.diagnostics(),
    }
