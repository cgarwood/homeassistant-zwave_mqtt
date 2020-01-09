"""Representation of Z-Wave switchs."""

import logging

from homeassistant.components.switch import SwitchDevice
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

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
        switch = ZWaveSwitch(value)

        async_add_entities([switch])

    async_dispatcher_connect(hass, "zwave_new_switch", async_add_switch)

    return True


class ZWaveSwitch(ZWaveDeviceEntity, SwitchDevice):
    """Representation of a Z-Wave switch."""

    @property
    def state(self):
        """Return the state of the switch."""
        if self.values.primary.value:
            return STATE_ON
        return STATE_OFF

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        self.values.primary.send_value(True)

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        self.values.primary.send_value(False)
