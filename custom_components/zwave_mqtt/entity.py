"""Generic Z-Wave Entity Classes."""

import copy
import logging

from openzwavemqtt.const import EVENT_VALUE_CHANGED

from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.entity import Entity

from . import const
from .const import DOMAIN, PLATFORMS
from .discovery import check_node_schema, check_value_schema

_LOGGER = logging.getLogger(__name__)


class ZWaveDeviceEntityValues:
    """Manages entity access to the underlying Z-Wave value objects."""

    def __init__(self, hass, options, schema, primary_value):
        """Initialize the values object with the passed entity schema."""
        self._hass = hass
        self._schema = copy.deepcopy(schema)
        self._values = {}
        self._entity = None
        self._entity_created = False
        self._options = options

        # Go through values listed in the discovery schema, initialize them,
        # and add a check to the schema to make sure the Instance matches.
        for name in self._schema[const.DISC_VALUES].keys():
            self._values[name] = None
            self._schema[const.DISC_VALUES][name][const.DISC_INSTANCE] = [
                primary_value.instance
            ]

        self._values[const.DISC_PRIMARY] = primary_value
        self._node = primary_value.node
        self._schema[const.DISC_NODE_ID] = [self._node.node_id]

        # Check values that have already been discovered for node
        # and see if they match the schema and need added to the entity.
        for value in self._node.values():
            self.check_value(value)

        # Check if all the _required_ values in the schema are present and
        # create the entity.
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

        # Make sure the node matches the schema for this entity.
        if not check_node_schema(value.node, self._schema):
            return

        # Go through the possible values for this entity defined by the schema.
        for name in self._values:
            # Skip if it's already been added.
            if self._values[name] is not None:
                continue
            # Skip if the value doesn't match the schema.
            if not check_value_schema(value, self._schema[const.DISC_VALUES][name]):
                continue

            # Add value to mapping.
            self._values[name] = value

            # If the entity has already been created, notify it of the new value.
            if self._entity:
                self._entity.value_added()

            # Check if entity has all required values and create the entity if needed.
            self._check_entity_ready()

    def _check_entity_ready(self):
        """Check if all required values are discovered and create entity."""
        # Abort if the entity has already been created
        if self._entity_created:
            return

        # Go through values defined in the schema and abort if a required value is missing.
        for name in self._schema[const.DISC_VALUES]:
            if self._values[name] is None and not self._schema[const.DISC_VALUES][
                name
            ].get(const.DISC_OPTIONAL):
                return

        # We have all the required values, so create the entity.
        component = self._schema[const.DISC_COMPONENT]

        _LOGGER.debug(
            "Adding Node_id=%s Generic_command_class=%s, "
            "Specific_command_class=%s, "
            "Command_class=%s, Index=%s, Value type=%s, "
            "Genre=%s as %s",
            self._node.node_id,
            self._node.node_generic,
            self._node.node_specific,
            self.primary.command_class,
            self.primary.index,
            self.primary.type,
            self.primary.genre,
            component,
        )
        self._entity_created = True
        if component in PLATFORMS:
            async_dispatcher_send(self._hass, f"zwave_new_{component}", self)


class ZWaveDeviceEntity(Entity):
    """Generic Entity Class for a Z-Wave Device."""

    def __init__(self, values):
        """Initilize a generic Z-Wave device entity."""
        self.values = values
        self.options = values._options
        self.values._entity = self

    @callback
    def value_changed(self, value):
        """Call when the value is changed."""
        if value.value_id_key in [v.value_id_key for v in self.values if v]:
            self.async_schedule_update_ha_state()

    def value_added(self):
        """Handle a new value for this entity."""
        pass

    async def async_added_to_hass(self):
        """Call when entity is added."""
        self.options.listen(EVENT_VALUE_CHANGED, self.value_changed)

    @property
    def device_info(self):
        """Return device information for the device registry."""
        return {
            "identifiers": {(DOMAIN, self.values.primary.node.node_id)},
            "name": f"{self.values.primary.node.node_manufacturer_name} {self.values.primary.node.node_product_name}",
            "manufacturer": self.values.primary.node.node_manufacturer_name,
            "model": self.values.primary.node.node_product_name,
        }

    @property
    def device_state_attributes(self):
        """Return the device specific state attributes."""
        attrs = {const.ATTR_NODE_ID: self.values.primary.node.node_id}

        return attrs

    @property
    def name(self):
        """Return the name of the entity."""
        return f"{self.values.primary.node.node_manufacturer_name} {self.values.primary.node.node_product_name}: {self.values.primary.label}"

    @property
    def unique_id(self):
        """Return the unique_id of the entity."""
        return f"{self.values.primary.node.id}-{self.values.primary.value_id_key}"
