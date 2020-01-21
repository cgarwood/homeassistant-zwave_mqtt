"""Representation of Z-Wave sensors."""

import logging

from homeassistant.components.sensor import DEVICE_CLASS_BATTERY
from homeassistant.const import TEMP_CELSIUS, TEMP_FAHRENHEIT
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN
from .entity import ZWaveDeviceEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Z-Wave sensor from config entry."""

    @callback
    def async_add_sensor(value):
        """Add Z-Wave Sensor."""

        # Basic Sensor types
        if isinstance(value.primary.value, (float, int)):
            sensor = ZWaveSensor(value)
        if isinstance(value.primary.value, dict):
            sensor = ZWaveListSensor(value)

        # Specific Sensor Types
        if value.primary.command_class == "COMMAND_CLASS_BATTERY":
            sensor = ZWaveBatterySensor(value)

        async_add_entities([sensor])

    async_dispatcher_connect(hass, "zwave_new_sensor", async_add_sensor)

    await hass.data[DOMAIN][config_entry.entry_id]["mark_platform_loaded"]("sensor")

    return True


class ZWaveSensor(ZWaveDeviceEntity):
    """Representation of a Z-Wave sensor."""

    @property
    def state(self):
        """Return state of the sensor."""
        return round(self.values.primary.value, 2)

    @property
    def unit_of_measurement(self):
        """Return unit of measurement the value is expressed in."""
        if self.values.primary.units == "C":
            return TEMP_CELSIUS
        if self.values.primary.units == "F":
            return TEMP_FAHRENHEIT

        return self.values.primary.units


class ZWaveListSensor(ZWaveDeviceEntity):
    """Representation of a Z-Wave list sensor."""

    @property
    def state(self):
        """Return the state of the sensor."""
        values = self.values.primary.value["List"]
        selected = self.values.primary.value["Selected"]
        match = self._find(values, "Label", selected)
        if match == -1:
            return None
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
