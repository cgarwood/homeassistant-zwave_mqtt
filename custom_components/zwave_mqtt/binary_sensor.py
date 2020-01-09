"""Representation of Z-Wave binary_sensors."""

import logging

from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .entity import ZWaveDeviceEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Old way of setting up Z-Wave platforms."""
    pass


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Z-Wave binary_sensor from config entry."""

    @callback
    def async_add_binary_sensor(value):
        """Add Z-Wave Binary Sensor."""
        binary_sensor = ZWaveBinarySensor(value)

        async_add_entities([binary_sensor])

    async_dispatcher_connect(hass, "zwave_new_binary_sensor", async_add_binary_sensor)

    return True


class ZWaveBinarySensor(ZWaveDeviceEntity, BinarySensorDevice):
    """Representation of a Z-Wave binary_sensor."""

    @property
    def is_on(self):
        """Return if the sensor is on or off."""
        return self.values.primary.value
