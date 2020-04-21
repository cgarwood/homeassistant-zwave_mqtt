"""Representation of Z-Wave sensors."""

import logging

from openzwavemqtt.const import CommandClass

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
        # Specific Sensor Types
        if value.primary.command_class == CommandClass.BATTERY:
            sensor = ZWaveBatterySensor(value)

        # Basic Sensor types
        elif isinstance(value.primary.value, (float, int)):
            sensor = ZWaveSensor(value)

        elif isinstance(value.primary.value, dict):
            sensor = ZWaveListSensor(value)

        else:
            _LOGGER.warning("Sensor not implemented for value %s", value.primary)
            return

        async_add_entities([sensor])

    async_dispatcher_connect(hass, "zwave_new_sensor", async_add_sensor)

    await hass.data[DOMAIN][config_entry.entry_id]["mark_platform_loaded"]("sensor")


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
        # We use the textbased value as it is more userfriendly that the integer
        return self.values.primary.value["Selected"]

    @property
    def state_attributes(self):
        """Return the device specific state attributes."""
        all_values = [item["Label"] for item in self.values.primary.value["List"]]
        return {"values": all_values}


class ZWaveBatterySensor(ZWaveSensor):
    """Representation of a Z-Wave battery sensor."""

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return DEVICE_CLASS_BATTERY
