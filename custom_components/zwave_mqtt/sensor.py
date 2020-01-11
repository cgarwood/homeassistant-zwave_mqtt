"""Representation of Z-Wave sensors."""

import logging

from openzwavemqtt.models.node import EVENT_NODE_CHANGED
from openzwavemqtt.models.node_statistics import EVENT_NODE_STATISTICS_CHANGED

from homeassistant.components.sensor import DEVICE_CLASS_BATTERY
from homeassistant.const import TEMP_CELSIUS, TEMP_FAHRENHEIT
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from . import const
from .const import DOMAIN
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

        # Basic Sensor types
        if isinstance(value.primary.value, (float, int)):
            sensor = ZWaveSensor(value)
        if isinstance(value.primary.value, dict):
            sensor = ZWaveListSensor(value)

        # Specific Sensor Types
        if value.primary.command_class == "COMMAND_CLASS_BATTERY":
            sensor = ZWaveBatterySensor(value)

        async_add_entities([sensor])

    @callback
    def async_add_node_sensor(node):
        sensor = ZWaveNodeStatisticsSensor(node)
        async_add_entities([sensor])

    async_dispatcher_connect(hass, "zwave_new_sensor", async_add_sensor)
    async_dispatcher_connect(hass, "zwave_new_node_sensor", async_add_node_sensor)

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


class ZWaveNodeStatisticsSensor(Entity):
    """Representation of a Z-Wave node status sensor."""

    def __init__(self, node):
        """Initilize a generic Z-Wave device entity."""
        self.node = node
        self.options = node.options
        self.attributes = {}
        self.statistics = {}

    @callback
    def stats_changed(self, stats):
        """Call when the statistics are changed."""
        self.statistics = stats
        stat_attributes = [
            "average_request_rtt",
            "average_response_rtt",
            "received_packets",
            "received_unsolicited",
            "received_dup_packets",
            "send_count",
            "sent_failed",
            "tx_time",
        ]

        for attr in stat_attributes:
            value = getattr(self.statistics, attr)
            if value:
                self.attributes[attr] = value

        self.async_schedule_update_ha_state()

    @callback
    def node_changed(self, node):
        """Call when the node is changed."""
        self.node = node
        node_attributes = [
            const.ATTR_AWAKE,
            const.ATTR_FAILED,
            const.ATTR_NODE_ID,
            const.ATTR_QUERY_STAGE,
            const.ATTR_ZWAVE_PLUS,
            "is_beaming",
            "is_routing",
        ]

        for attr in node_attributes:
            value = getattr(self.node, attr)
            self.attributes[attr] = value

        self.async_schedule_update_ha_state()

    async def async_added_to_hass(self):
        """Call when entity is added."""
        self.options.listen(EVENT_NODE_STATISTICS_CHANGED, self.stats_changed)
        self.options.listen(EVENT_NODE_CHANGED, self.node_changed)
        self.node_changed(self.node)
        self.stats_changed(self.node.get_statistics())

    @property
    def device_info(self):
        """Return device information for the device registry."""
        return {
            "identifiers": {(DOMAIN, self.node.node_id)},
            "name": f"{self.node.node_manufacturer_name} {self.node.node_product_name}",
            "manufacturer": self.node.node_manufacturer_name,
            "model": self.node.node_product_name,
        }

    @property
    def device_state_attributes(self):
        """Return the device specific state attributes."""
        self.attributes[const.ATTR_NODE_ID] = self.node.node_id
        return self.attributes

    @property
    def name(self):
        """Return the name of the entity."""
        return f"{self.node.node_manufacturer_name} {self.node.node_product_name}: Node Status"

    @property
    def state(self):
        """Return the state of the entity."""
        return self.node.node_query_stage

    @property
    def unique_id(self):
        """Return the unique_id of the entity."""
        return f"node-{self.node.id}"
