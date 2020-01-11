"""The zwave_mqtt integration."""
import asyncio
import json
import logging

from openzwavemqtt import OZWManager, OZWOptions
from openzwavemqtt.const import (
    EVENT_NODE_ADDED,
    EVENT_NODE_CHANGED,
    EVENT_VALUE_ADDED,
    EVENT_VALUE_CHANGED,
)
import voluptuous as vol

from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_START
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send

from . import const
from .const import DATA_NODES, DATA_VALUES, DOMAIN, PLATFORMS, TOPIC_OPENZWAVE
from .discovery import DISCOVERY_SCHEMAS, check_node_schema, check_value_schema
from .entity import ZWaveDeviceEntityValues

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)
DATA_DEVICES = "zwave-mqtt-devices"


async def async_setup(hass: HomeAssistant, config: dict):
    """Old method to set up the zwave_mqtt component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up zwave_mqtt from a config entry."""

    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][DATA_NODES] = {}
    hass.data[DOMAIN][DATA_VALUES] = {}

    def send_message(topic, payload):
        _LOGGER.debug("sending message to topic %s", topic)
        mqtt.async_publish(hass, topic, json.dumps(payload))

    options = OZWOptions(send_message=send_message, topic_prefix=f"{TOPIC_OPENZWAVE}/")
    manager = OZWManager(options)

    async def receive_message(msg):
        manager.receive_message(msg.topic, msg.payload)

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    # Subscribe to topic
    async def _connect(self):
        await mqtt.async_subscribe(hass, f"{TOPIC_OPENZWAVE}/#", receive_message)

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, _connect)

    def node_added(node):
        _LOGGER.info("NODE ADDED: %s - node id %s", node, node.id)
        hass.data[DOMAIN][DATA_NODES][node.id] = node
        hass.data[DOMAIN][DATA_VALUES][node.id] = []

        # Create node statistics sensor
        async_dispatcher_send(hass, "zwave_new_node_sensor", node)

    def node_changed(node):
        _LOGGER.info("node changed: %s", node)
        hass.data[DOMAIN][DATA_NODES][node.id] = node

    def value_added(value):
        node = value.node
        node_id = value.node.node_id

        # temporary if statement to cut down on number of debug log lines
        if value.command_class not in [
            "COMMAND_CLASS_CONFIGURATION",
            "COMMAND_CLASS_VERSION",
        ]:
            _LOGGER.debug(
                "Value added: node %s - value label %s - value %s -- id %s -- cc %s",
                value.node.id,
                value.label,
                value.value,
                value.value_id_key,
                value.command_class,
            )

        if node_id not in hass.data[DOMAIN][DATA_VALUES]:
            _LOGGER.warning("Got value added for non-existent node id %s", node_id)
            return

        data_values = hass.data[DOMAIN][DATA_VALUES][node_id]

        # Check if this value should be tracked by an existing entity
        for values in data_values:
            values.check_value(value)

        # Run discovery on it and see if any entities need created
        for schema in DISCOVERY_SCHEMAS:
            if not check_node_schema(node, schema):
                continue
            if not check_value_schema(
                value, schema[const.DISC_VALUES][const.DISC_PRIMARY]
            ):
                continue

            values = ZWaveDeviceEntityValues(hass, options, schema, value)

            # We create a new list and update the reference here so that
            # the list can be safely iterated over in the main thread
            hass.data[DOMAIN][DATA_VALUES][node_id] = data_values + [values]

    def value_changed(value):
        _LOGGER.debug(
            "value changed - node %s - value label %s - value %s",
            value.node,
            value.label,
            value.value,
        )

    # Listen to events for node and value changes
    options.listen(EVENT_NODE_ADDED, node_added)
    options.listen(EVENT_VALUE_ADDED, value_added)
    options.listen(EVENT_NODE_CHANGED, node_changed)
    options.listen(EVENT_VALUE_CHANGED, value_changed)

    # Register Services
    # def add_node(service_data):
    #    manager.get_instance("1").add_node(False)

    # def cancel_command(service_data):
    #    manager.get_instance("1").cancel_command()

    # hass.services.async_register(DOMAIN, "add_node", add_node)
    # hass.services.async_register(DOMAIN, "cancel_command", cancel_command)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
