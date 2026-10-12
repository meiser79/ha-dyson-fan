"""Shared test fixtures for Dyson Fan."""

from __future__ import annotations

from collections.abc import Iterator
from unittest.mock import AsyncMock, patch

import pytest

EMITTER_ENTITY_ID = "infrared.test_emitter"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Allow Home Assistant to load this repository's custom integration."""


@pytest.fixture(autouse=True)
def infrared_emitter() -> Iterator[AsyncMock]:
    """Provide one infrared emitter; the mock records every sent command."""
    with (
        patch(
            "homeassistant.components.infrared.async_get_emitters",
            return_value=[EMITTER_ENTITY_ID],
        ),
        patch(
            "homeassistant.components.infrared.async_send_command",
            new_callable=AsyncMock,
        ) as send,
    ):
        yield send
