"""Helpers for tests."""
import json
import logging
from pathlib import Path

from asynctest import patch
import pytest

from homeassistant import config_entries, core

from tests.common import mock_storage

logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
async def hass(loop, hass_storage, sent_messages):
    """Home Assistant instance."""
    hass = core.HomeAssistant()

    hass.config.config_dir = str(Path(__file__).parent.parent)
    hass.config.skip_pip = True

    hass.config_entries = config_entries.ConfigEntries(hass, {})
    await hass.config_entries.async_initialize()
    return hass


@pytest.fixture
def hass_storage():
    """Fixture to mock storage."""
    with mock_storage() as stored_data:
        yield stored_data


@pytest.fixture
def sent_messages():
    """Fixture to capture sent messages."""
    sent_messages = []

    with patch(
        "homeassistant.components.mqtt.async_publish",
        side_effect=lambda hass, topic, payload: sent_messages.append(
            {"topic": topic, "payload": json.loads(payload)}
        ),
    ):
        yield sent_messages
