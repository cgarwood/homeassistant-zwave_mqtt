"""Generic Z-Wave Entity Classes."""

import copy
import logging

from homeassistant.core import callback
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, PLATFORMS
from .discovery import check_node_schema, check_value_schema
from . import const

_LOGGER = logging.getLogger(__name__)


class ZWaveDeviceEntityValues:
    """Manages entity access to the underlying zwave value objects."""

    def __init__(self, hass, schema, primary_value):
        """Initialize the values object with the passed entity schema."""
        self._hass = hass
        self._schema = copy.deepcopy(schema)
        self._values = {}
        self._entity = None

        for name in self._schema[const.DISC_VALUES].keys():
            self._values[name] = None
            self._schema[const.DISC_VALUES][name][const.DISC_INSTANCE] = [
                primary_value.instance
            ]

        self._values[const.DISC_PRIMARY] = primary_value
        self._node = primary_value.node
        self._schema[const.DISC_NODE_ID] = [self._node.node_id]

        # Check values that have already been discovered for node
        for value in self._node.values():
            self.check_value(value)

        self._check_entity_ready()

    def __getattr__(self, name):
        """Get the specified value for this entity."""
        return self._values[name]

    def __iter__(self):
        """Allow iteration over all values."""
        return iter(self._values.values())

    def check_value(self, value):
        """Check if the new value matches a missing value for this entity.

        If a match is found, it is added to the values mapping.
        """
        if not check_node_schema(value.node, self._schema):
            return
        for name in self._values:
            if self._values[name] is not None:
                continue
            if not check_value_schema(value, self._schema[const.DISC_VALUES][name]):
                continue
            self._values[name] = value
            if self._entity:
                self._entity.value_added()
                self._entity.value_changed()

            self._check_entity_ready()

    def _check_entity_ready(self):
        """Check if all required values are discovered and create entity."""
        if self._entity is not None:
            return

        for name in self._schema[const.DISC_VALUES]:
            if self._values[name] is None and not self._schema[const.DISC_VALUES][
                name
            ].get(const.DISC_OPTIONAL):
                return

        component = self._schema[const.DISC_COMPONENT]

        # Configure node
        _LOGGER.debug(
            "Adding Node_id=%s Generic_command_class=%s, "
            "Specific_command_class=%s, "
            "Command_class=%s, Value type=%s, "
            "Genre=%s as %s",
            self._node.node_id,
            self._node.node_generic,
            self._node.node_specific,
            self.primary.command_class,
            self.primary.type,
            self.primary.genre,
            component,
        )

        if component in PLATFORMS:
            async_dispatcher_send(self._hass, f"zwave_new_{component}", self._values)


class ZWaveDeviceEntity(Entity):
    """Generic Entity Class for a Z-Wave Device."""

    def __init__(self, value):
        self._value = value

    async def async_added_to_hass(self):
        async_dispatcher_connect(
            self.hass,
            f"zwave_value_updated_{self._value.value_id_key}",
            self.value_changed,
        )

    @callback
    def value_changed(self, value):
        """Call when the value is changed."""
        self._value = value
        self.async_schedule_update_ha_state()

    @property
    def name(self):
        return f"{self._value.node.node_manufacturer_name} {self._value.node.node_product_name}: {self._value.label}"

    @property
    def state(self):
        return self._value.value

    @property
    def unique_id(self):
        return f"{self._value.node.id}-{self._value.value_id_key}"
