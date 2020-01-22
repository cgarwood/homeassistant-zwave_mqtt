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
from openzwavemqtt.models.value import OZWValue
import voluptuous as vol

from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback

from . import const
from .const import DOMAIN, PLATFORMS, TOPIC_OPENZWAVE
from .discovery import DISCOVERY_SCHEMAS, check_node_schema, check_value_schema
from .entity import ZWaveDeviceEntityValues
from .services import ZWaveServices

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)
DATA_DEVICES = "zwave-mqtt-devices"


async def async_setup(hass: HomeAssistant, config: dict):
    """Initialize basic config of zwave_mqtt component."""
    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up zwave_mqtt from a config entry."""

    @callback
    def async_receive_message(msg):
        manager.receive_message(msg.topic, msg.payload)

    platforms_loaded = []

    async def mark_platform_loaded(platform):
        platforms_loaded.append(platform)

        if len(platforms_loaded) != len(PLATFORMS):
            return

        hass.data[DOMAIN][entry.entry_id]["unsubscribe"] = await mqtt.async_subscribe(
            hass, f"{TOPIC_OPENZWAVE}/#", async_receive_message
        )

    hass.data[DOMAIN][entry.entry_id] = {"mark_platform_loaded": mark_platform_loaded}

    data_nodes = {}
    data_values = {}

    @callback
    def send_message(topic, payload):
        _LOGGER.debug("sending message to topic %s", topic)
        mqtt.async_publish(hass, topic, json.dumps(payload))

    options = OZWOptions(send_message=send_message, topic_prefix=f"{TOPIC_OPENZWAVE}/")
    manager = OZWManager(options)

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    @callback
    def async_node_added(node):
        _LOGGER.info("NODE ADDED: %s - node id %s", node, node.id)
        data_nodes[node.id] = node
        data_values[node.id] = []

    @callback
    def async_node_changed(node):
        _LOGGER.info("NODE CHANGED: %s", node)
        data_nodes[node.id] = node

    @callback
    def async_value_added(value):
        node = value.node
        node_id = value.node.node_id

        # temporary if statement to cut down on number of debug log lines
        if value.command_class not in [
            "COMMAND_CLASS_CONFIGURATION",
            "COMMAND_CLASS_VERSION",
        ]:
            _LOGGER.debug(
                "VALUE ADDED: node %s - value label %s - value %s -- id %s -- cc %s",
                value.node.id,
                value.label,
                value.value,
                value.value_id_key,
                value.command_class,
            )

        node_data_values = data_values[node_id]

        # Check if this value should be tracked by an existing entity
        for values in node_data_values:
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
            data_values[node_id] = node_data_values + [values]

    @callback
    def async_value_changed(value):
        _LOGGER.debug(
            "VALUE CHANGED: node %s - value label %s - value %s",
            value.node,
            value.label,
            value.value,
        )
        # Handle a scene activation message
        if value.command_class in [
            "COMMAND_CLASS_SCENE_ACTIVATION",
            "COMMAND_CLASS_CENTRAL_SCENE",
        ]:
            handle_scene_activated(hass, value)
            return

    # Listen to events for node and value changes
    options.listen(EVENT_NODE_ADDED, async_node_added)
    options.listen(EVENT_VALUE_ADDED, async_value_added)
    options.listen(EVENT_NODE_CHANGED, async_node_changed)
    options.listen(EVENT_VALUE_CHANGED, async_value_changed)

    # Register Services
    services = ZWaveServices(hass, manager, data_nodes)
    services.register()

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
    if not unload_ok:
        return False

    hass.data[DOMAIN][entry.entry_id]["unsubscribe"]()
    hass.data[DOMAIN].pop(entry.entry_id)

    return True


@callback
def handle_scene_activated(hass: HomeAssistant, scene_value: OZWValue):
    """Handle a (central) scene activation message."""
    if scene_value.command_class == "COMMAND_CLASS_SCENE_ACTIVATION":
        # legacy/network scene
        scene_id = scene_value.value
        label = scene_value.label
    else:
        # central scene command
        label = scene_value.value["Selected"]
        for item in scene_value.value["List"]:
            if item["Label"] == label:
                scene_id = item["Value"]
                break
    _LOGGER.debug(
        "Scene activated - node: %s - scene_id: %s - label: %s",
        scene_value.node.id,
        scene_id,
        label,
    )
    # Simply forward it to the hass event bus
    hass.bus.async_fire(
        const.EVENT_SCENE_ACTIVATED,
        {
            const.ATTR_NODE_ID: scene_value.node.id,
            const.ATTR_SCENE_ID: scene_id,
            const.ATTR_SCENE_LABEL: label,
        },
    )
