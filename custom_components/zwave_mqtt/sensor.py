"""Representation of Z-Wave sensors."""

import logging

from homeassistant.components.sensor import DEVICE_CLASS_BATTERY
from homeassistant.const import TEMP_CELSIUS, TEMP_FAHRENHEIT
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

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

        # Basic Sensor types
        if isinstance(_value.value, (float, int)):
            sensor = ZWaveSensor(_value)
        if isinstance(_value.value, dict):
            sensor = ZWaveListSensor(_value)

        # Specific Sensor Types
        if _value.command_class == "COMMAND_CLASS_BATTERY":
            sensor = ZWaveBatterySensor(_value)

        async_add_entities([sensor])

    async_dispatcher_connect(hass, "zwave_new_sensor", async_add_sensor)

    return True


class ZWaveSensor(ZWaveDeviceEntity):
    """Representation of a Z-Wave sensor."""

    @property
    def state(self):
        """Return state of the sensor."""
        return round(self._value.value, 2)

    @property
    def unit_of_measurement(self):
        """Return unit of measurement the value is expressed in."""
        if self._value.units == "C":
            return TEMP_CELSIUS
        if self._value.units == "F":
            return TEMP_FAHRENHEIT

        return self._value.units


class ZWaveListSensor(ZWaveDeviceEntity):
    """Representation of a Z-Wave list sensor."""

    @property
    def state(self):
        """Return the state of the sensor."""
        values = self._value.value["List"]
        selected = self._value.value["Selected"]
        match = self._find(values, "Label", selected)
        return values[match]["Value"]

    def _find(self, lst, key, value):
        """Search list for a value."""
        for i, dic in enumerate(lst):
            if dic[key] == value:
                return i
        return -1


class ZWaveBatterySensor(ZWaveSensor):
    """Representation of a Z-Wave battery sensor."""

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return DEVICE_CLASS_BATTERY
