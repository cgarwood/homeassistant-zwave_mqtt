"""Representation of Z-Wave binary_sensors."""

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
    """Set up Z-Wave binary_sensor from config entry."""

    @callback
    def async_add_binary_sensor(value):
        """Add Z-Wave Binary Sensor."""
        _value = value["primary"]
        _LOGGER.info("adding binary_sensor from value: %s", _value.__dict__)
        binary_sensor = ZWaveBinarySensor(_value)

        async_add_entities([binary_sensor])

    async_dispatcher_connect(hass, "zwave_new_binary_sensor", async_add_binary_sensor)
    _LOGGER.warning("created binary_sensor listener")

    return True


class ZWaveBinarySensor(ZWaveDeviceEntity):
    """Representation of a Z-Wave binary_sensor."""

    @property
    def is_on(self):
        return self._value.value

    @property
    def state(self):
        return STATE_ON if self.is_on else STATE_OFF

    @property
    def unit_of_measurement(self):
        return self._value.units
