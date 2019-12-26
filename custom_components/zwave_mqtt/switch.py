"""Representation of Z-Wave switchs."""

import logging

from homeassistant.const import STATE_ON, STATE_OFF
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN, DATA_NODES, DATA_VALUES, TOPIC_OPENZWAVE
from .entity import ZWaveDeviceEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Old way of setting up Z-Wave platforms."""
    pass


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Z-Wave switch from config entry."""

    @callback
    def async_add_switch(value):
        """Add Z-Wave Switch."""
        _value = value["primary"]
        _LOGGER.info("adding switch from value: %s", _value.__dict__)
        switch = ZWaveSwitch(_value)

        async_add_entities([switch])

    async_dispatcher_connect(hass, "zwave_new_switch", async_add_switch)
    _LOGGER.warning("connected switch listener")

    return True


class ZWaveSwitch(ZWaveDeviceEntity):
    """Representation of a Z-Wave switch."""

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._value.value

    @property
    def state(self):
        if self._value.value:
            return STATE_ON
        return STATE_OFF

    async def async_turn_on(self):
        self._value.send_value(True)

    async def async_turn_off(self):
        self._value.send_value(False)
