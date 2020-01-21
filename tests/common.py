"""Helpers for tests."""
from contextlib import contextmanager
import json
import logging
from pathlib import Path
from unittest.mock import Mock

from asynctest import patch
from custom_components.zwave_mqtt.const import DOMAIN

from homeassistant import config_entries
from homeassistant.helpers import storage

_LOGGER = logging.getLogger(__name__)


@contextmanager
def mock_storage(data=None):
    """Mock storage.

    Data is a dict {'key': {'version': version, 'data': data}}

    Written data will be converted to JSON to ensure JSON parsing works.
    """
    if data is None:
        data = {}

    orig_load = storage.Store._async_load

    async def mock_async_load(store):
        """Mock version of load."""
        if store._data is None:
            # No data to load
            if store.key not in data:
                return None

            mock_data = data.get(store.key)

            if "data" not in mock_data or "version" not in mock_data:
                _LOGGER.error('Mock data needs "version" and "data"')
                raise ValueError('Mock data needs "version" and "data"')

            store._data = mock_data

        # Route through original load so that we trigger migration
        loaded = await orig_load(store)
        _LOGGER.info("Loading data for %s: %s", store.key, loaded)
        return loaded

    def mock_write_data(store, path, data_to_write):
        """Mock version of write data."""
        _LOGGER.info("Writing data to %s: %s", store.key, data_to_write)
        # To ensure that the data can be serialized
        data[store.key] = json.loads(json.dumps(data_to_write, cls=store._encoder))

    with patch(
        "homeassistant.helpers.storage.Store._async_load",
        side_effect=mock_async_load,
        autospec=True,
    ), patch(
        "homeassistant.helpers.storage.Store._write_data",
        side_effect=mock_write_data,
        autospec=True,
    ):
        yield data


async def setup_zwave(hass, fixture=None):
    """Set up Z-Wave and load a dump."""
    hass.config.components.add("mqtt")

    with patch("homeassistant.components.mqtt.async_subscribe") as mock_subscribe:
        await hass.config_entries.async_add(
            config_entries.ConfigEntry(
                1,
                DOMAIN,
                "Z-Wave",
                {},
                config_entries.SOURCE_USER,
                config_entries.CONN_CLASS_LOCAL_PUSH,
                {},
            )
        )
        await hass.async_block_till_done()

    assert "zwave_mqtt" in hass.config.components
    assert len(mock_subscribe.mock_calls) == 1
    receive_message = mock_subscribe.mock_calls[0][1][2]

    if fixture is not None:
        data = Path(__file__).parent / "fixtures" / fixture

        with data.open("rt") as fp:
            for line in fp:
                topic, payload = line.strip().split(",", 1)
                receive_message(Mock(topic=topic, payload=payload))

        await hass.async_block_till_done()

    return receive_message
