"""Representation of Z-Wave sensors."""

import logging

from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN, DATA_NODES, DATA_VALUES, TOPIC_OPENZWAVE
from .entity import ZWaveDeviceEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Old way of setting up Z-Wave platforms."""
    pass


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Z-Wave sensor from config entry."""

    @callback
    def async_add_sensor(value):
        """Add Z-Wave Sensor."""
        _value = value["primary"]
        _LOGGER.info("adding sensor from value: %s", _value.__dict__)
        if isinstance(_value.value, (float, int)):
            sensor = ZWaveSensor(_value)
        if isinstance(_value.value, dict):
            sensor = ZWaveListSensor(_value)

        async_add_entities([sensor])

    async_dispatcher_connect(hass, "zwave_new_sensor", async_add_sensor)
    _LOGGER.warning("created sensor listener")

    return True


class ZWaveSensor(ZWaveDeviceEntity):
    """Representation of a Z-Wave sensor."""

    @property
    def state(self):
        return round(self._value.value, 2)

    @property
    def unit_of_measurement(self):
        return self._value.units


class ZWaveListSensor(ZWaveDeviceEntity):
    @property
    def state(self):
        values = self._value.value["List"]
        selected = self._value.value["Selected"]
        match = self._find(values, "Label", selected)
        return values[match]["Value"]

    def _find(self, lst, key, value):
        for i, dic in enumerate(lst):
            if dic[key] == value:
                return i
        return -1
