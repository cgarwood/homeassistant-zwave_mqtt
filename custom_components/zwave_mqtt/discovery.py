import logging

from . import const

_LOGGER = logging.getLogger(__name__)

DEFAULT_VALUES_SCHEMA = {
    "power": {
        const.DISC_SCHEMAS: [
            {
                const.DISC_COMMAND_CLASS: [const.COMMAND_CLASS_SENSOR_MULTILEVEL],
                const.DISC_INDEX: [const.INDEX_SENSOR_MULTILEVEL_POWER],
            },
            {
                const.DISC_COMMAND_CLASS: [const.COMMAND_CLASS_METER],
                const.DISC_INDEX: [const.INDEX_METER_POWER],
            },
        ],
        const.DISC_OPTIONAL: True,
    }
}

DISCOVERY_SCHEMAS = [
    {
        const.DISC_COMPONENT: "binary_sensor",
        const.DISC_GENERIC_DEVICE_CLASS: [
            const.GENERIC_TYPE_ENTRY_CONTROL,
            const.GENERIC_TYPE_SENSOR_ALARM,
            const.GENERIC_TYPE_SENSOR_BINARY,
            const.GENERIC_TYPE_SWITCH_BINARY,
            const.GENERIC_TYPE_METER,
            const.GENERIC_TYPE_SENSOR_MULTILEVEL,
            const.GENERIC_TYPE_SWITCH_MULTILEVEL,
            const.GENERIC_TYPE_SENSOR_NOTIFICATION,
            const.GENERIC_TYPE_THERMOSTAT,
        ],
        const.DISC_VALUES: dict(
            DEFAULT_VALUES_SCHEMA,
            **{
                const.DISC_PRIMARY: {
                    const.DISC_COMMAND_CLASS: [const.COMMAND_CLASS_SENSOR_BINARY],
                    const.DISC_TYPE: const.TYPE_BOOL,
                    const.DISC_GENRE: const.GENRE_USER,
                },
                "off_delay": {
                    const.DISC_COMMAND_CLASS: [const.COMMAND_CLASS_CONFIGURATION],
                    const.DISC_INDEX: [9],
                    const.DISC_OPTIONAL: True,
                },
            },
        ),
    },
    {
        const.DISC_COMPONENT: "climate",
        const.DISC_GENERIC_DEVICE_CLASS: [
            const.GENERIC_TYPE_THERMOSTAT,
            const.GENERIC_TYPE_SENSOR_MULTILEVEL,
        ],
        const.DISC_VALUES: dict(
            DEFAULT_VALUES_SCHEMA,
            **{
                const.DISC_PRIMARY: {
                    const.DISC_COMMAND_CLASS: [const.COMMAND_CLASS_THERMOSTAT_SETPOINT]
                },
                "temperature": {
                    const.DISC_COMMAND_CLASS: [const.COMMAND_CLASS_SENSOR_MULTILEVEL],
                    const.DISC_INDEX: [const.INDEX_SENSOR_MULTILEVEL_TEMPERATURE],
                    const.DISC_OPTIONAL: True,
                },
                "mode": {
                    const.DISC_COMMAND_CLASS: [const.COMMAND_CLASS_THERMOSTAT_MODE],
                    const.DISC_OPTIONAL: True,
                },
                "fan_mode": {
                    const.DISC_COMMAND_CLASS: [const.COMMAND_CLASS_THERMOSTAT_FAN_MODE],
                    const.DISC_OPTIONAL: True,
                },
                "operating_state": {
                    const.DISC_COMMAND_CLASS: [
                        const.COMMAND_CLASS_THERMOSTAT_OPERATING_STATE
                    ],
                    const.DISC_OPTIONAL: True,
                },
                "fan_action": {
                    const.DISC_COMMAND_CLASS: [
                        const.COMMAND_CLASS_THERMOSTAT_FAN_ACTION
                    ],
                    const.DISC_OPTIONAL: True,
                },
                "zxt_120_swing_mode": {
                    const.DISC_COMMAND_CLASS: [const.COMMAND_CLASS_CONFIGURATION],
                    const.DISC_INDEX: [33],
                    const.DISC_OPTIONAL: True,
                },
            },
        ),
    },
    {
        const.DISC_COMPONENT: "cover",  # Rollershutter
        const.DISC_GENERIC_DEVICE_CLASS: [
            const.GENERIC_TYPE_SWITCH_MULTILEVEL,
            const.GENERIC_TYPE_ENTRY_CONTROL,
        ],
        const.DISC_SPECIFIC_DEVICE_CLASS: [
            const.SPECIFIC_TYPE_CLASS_A_MOTOR_CONTROL,
            const.SPECIFIC_TYPE_CLASS_B_MOTOR_CONTROL,
            const.SPECIFIC_TYPE_CLASS_C_MOTOR_CONTROL,
            const.SPECIFIC_TYPE_MOTOR_MULTIPOSITION,
            const.SPECIFIC_TYPE_SECURE_BARRIER_ADDON,
            const.SPECIFIC_TYPE_SECURE_DOOR,
        ],
        const.DISC_VALUES: dict(
            DEFAULT_VALUES_SCHEMA,
            **{
                const.DISC_PRIMARY: {
                    const.DISC_COMMAND_CLASS: [const.COMMAND_CLASS_SWITCH_MULTILEVEL],
                    const.DISC_GENRE: const.GENRE_USER,
                },
                "open": {
                    const.DISC_COMMAND_CLASS: [const.COMMAND_CLASS_SWITCH_MULTILEVEL],
                    const.DISC_INDEX: [const.INDEX_SWITCH_MULTILEVEL_BRIGHT],
                    const.DISC_OPTIONAL: True,
                },
                "close": {
                    const.DISC_COMMAND_CLASS: [const.COMMAND_CLASS_SWITCH_MULTILEVEL],
                    const.DISC_INDEX: [const.INDEX_SWITCH_MULTILEVEL_DIM],
                    const.DISC_OPTIONAL: True,
                },
            },
        ),
    },
    {
        const.DISC_COMPONENT: "cover",  # Garage Door Switch
        const.DISC_GENERIC_DEVICE_CLASS: [
            const.GENERIC_TYPE_SWITCH_MULTILEVEL,
            const.GENERIC_TYPE_ENTRY_CONTROL,
        ],
        const.DISC_SPECIFIC_DEVICE_CLASS: [
            const.SPECIFIC_TYPE_CLASS_A_MOTOR_CONTROL,
            const.SPECIFIC_TYPE_CLASS_B_MOTOR_CONTROL,
            const.SPECIFIC_TYPE_CLASS_C_MOTOR_CONTROL,
            const.SPECIFIC_TYPE_MOTOR_MULTIPOSITION,
            const.SPECIFIC_TYPE_SECURE_BARRIER_ADDON,
            const.SPECIFIC_TYPE_SECURE_DOOR,
        ],
        const.DISC_VALUES: dict(
            DEFAULT_VALUES_SCHEMA,
            **{
                const.DISC_PRIMARY: {
                    const.DISC_COMMAND_CLASS: [const.COMMAND_CLASS_SWITCH_BINARY],
                    const.DISC_GENRE: const.GENRE_USER,
                }
            },
        ),
    },
    {
        const.DISC_COMPONENT: "cover",  # Garage Door Barrier
        const.DISC_GENERIC_DEVICE_CLASS: [
            const.GENERIC_TYPE_SWITCH_MULTILEVEL,
            const.GENERIC_TYPE_ENTRY_CONTROL,
        ],
        const.DISC_SPECIFIC_DEVICE_CLASS: [
            const.SPECIFIC_TYPE_CLASS_A_MOTOR_CONTROL,
            const.SPECIFIC_TYPE_CLASS_B_MOTOR_CONTROL,
            const.SPECIFIC_TYPE_CLASS_C_MOTOR_CONTROL,
            const.SPECIFIC_TYPE_MOTOR_MULTIPOSITION,
            const.SPECIFIC_TYPE_SECURE_BARRIER_ADDON,
            const.SPECIFIC_TYPE_SECURE_DOOR,
        ],
        const.DISC_VALUES: dict(
            DEFAULT_VALUES_SCHEMA,
            **{
                const.DISC_PRIMARY: {
                    const.DISC_COMMAND_CLASS: [const.COMMAND_CLASS_BARRIER_OPERATOR],
                    const.DISC_INDEX: [const.INDEX_BARRIER_OPERATOR_LABEL],
                }
            },
        ),
    },
    {
        const.DISC_COMPONENT: "fan",
        const.DISC_GENERIC_DEVICE_CLASS: [const.GENERIC_TYPE_SWITCH_MULTILEVEL],
        const.DISC_SPECIFIC_DEVICE_CLASS: [const.SPECIFIC_TYPE_FAN_SWITCH],
        const.DISC_VALUES: dict(
            DEFAULT_VALUES_SCHEMA,
            **{
                const.DISC_PRIMARY: {
                    const.DISC_COMMAND_CLASS: [const.COMMAND_CLASS_SWITCH_MULTILEVEL],
                    const.DISC_INDEX: [const.INDEX_SWITCH_MULTILEVEL_LEVEL],
                    const.DISC_TYPE: const.TYPE_BYTE,
                }
            },
        ),
    },
    {
        const.DISC_COMPONENT: "light",
        const.DISC_GENERIC_DEVICE_CLASS: [
            const.GENERIC_TYPE_SWITCH_MULTILEVEL,
            const.GENERIC_TYPE_SWITCH_REMOTE,
        ],
        const.DISC_SPECIFIC_DEVICE_CLASS: [
            const.SPECIFIC_TYPE_POWER_SWITCH_MULTILEVEL,
            const.SPECIFIC_TYPE_SCENE_SWITCH_MULTILEVEL,
            const.SPECIFIC_TYPE_NOT_USED,
        ],
        const.DISC_VALUES: dict(
            DEFAULT_VALUES_SCHEMA,
            **{
                const.DISC_PRIMARY: {
                    const.DISC_COMMAND_CLASS: [const.COMMAND_CLASS_SWITCH_MULTILEVEL],
                    const.DISC_INDEX: [const.INDEX_SWITCH_MULTILEVEL_LEVEL],
                    const.DISC_TYPE: const.TYPE_BYTE,
                },
                "dimming_duration": {
                    const.DISC_COMMAND_CLASS: [const.COMMAND_CLASS_SWITCH_MULTILEVEL],
                    const.DISC_INDEX: [const.INDEX_SWITCH_MULTILEVEL_DURATION],
                    const.DISC_OPTIONAL: True,
                },
                "color": {
                    const.DISC_COMMAND_CLASS: [const.COMMAND_CLASS_SWITCH_COLOR],
                    const.DISC_INDEX: [const.INDEX_SWITCH_COLOR_COLOR],
                    const.DISC_OPTIONAL: True,
                },
                "color_channels": {
                    const.DISC_COMMAND_CLASS: [const.COMMAND_CLASS_SWITCH_COLOR],
                    const.DISC_INDEX: [const.INDEX_SWITCH_COLOR_CHANNELS],
                    const.DISC_OPTIONAL: True,
                },
            },
        ),
    },
    {
        const.DISC_COMPONENT: "lock",
        const.DISC_GENERIC_DEVICE_CLASS: [const.GENERIC_TYPE_ENTRY_CONTROL],
        const.DISC_SPECIFIC_DEVICE_CLASS: [
            const.SPECIFIC_TYPE_DOOR_LOCK,
            const.SPECIFIC_TYPE_ADVANCED_DOOR_LOCK,
            const.SPECIFIC_TYPE_SECURE_KEYPAD_DOOR_LOCK,
            const.SPECIFIC_TYPE_SECURE_LOCKBOX,
        ],
        const.DISC_VALUES: dict(
            DEFAULT_VALUES_SCHEMA,
            **{
                const.DISC_PRIMARY: {
                    const.DISC_COMMAND_CLASS: [const.COMMAND_CLASS_DOOR_LOCK],
                    const.DISC_INDEX: [const.INDEX_DOOR_LOCK_LOCK],
                },
                "access_control": {
                    const.DISC_COMMAND_CLASS: [const.COMMAND_CLASS_ALARM],
                    const.DISC_INDEX: [const.INDEX_ALARM_ACCESS_CONTROL],
                    const.DISC_OPTIONAL: True,
                },
                "alarm_type": {
                    const.DISC_COMMAND_CLASS: [const.COMMAND_CLASS_ALARM],
                    const.DISC_INDEX: [const.INDEX_ALARM_TYPE],
                    const.DISC_OPTIONAL: True,
                },
                "alarm_level": {
                    const.DISC_COMMAND_CLASS: [const.COMMAND_CLASS_ALARM],
                    const.DISC_INDEX: [const.INDEX_ALARM_LEVEL],
                    const.DISC_OPTIONAL: True,
                },
                "v2btze_advanced": {
                    const.DISC_COMMAND_CLASS: [const.COMMAND_CLASS_CONFIGURATION],
                    const.DISC_INDEX: [12],
                    const.DISC_OPTIONAL: True,
                },
            },
        ),
    },
    {
        const.DISC_COMPONENT: "sensor",
        const.DISC_VALUES: dict(
            DEFAULT_VALUES_SCHEMA,
            **{
                const.DISC_PRIMARY: {
                    const.DISC_COMMAND_CLASS: [
                        const.COMMAND_CLASS_SENSOR_MULTILEVEL,
                        const.COMMAND_CLASS_METER,
                        const.COMMAND_CLASS_ALARM,
                        const.COMMAND_CLASS_SENSOR_ALARM,
                        const.COMMAND_CLASS_INDICATOR,
                        const.COMMAND_CLASS_BATTERY,
                    ],
                    const.DISC_GENRE: const.GENRE_USER,
                }
            },
        ),
    },
    {
        const.DISC_COMPONENT: "switch",
        const.DISC_GENERIC_DEVICE_CLASS: [
            const.GENERIC_TYPE_METER,
            const.GENERIC_TYPE_SENSOR_ALARM,
            const.GENERIC_TYPE_SENSOR_BINARY,
            const.GENERIC_TYPE_SWITCH_BINARY,
            const.GENERIC_TYPE_ENTRY_CONTROL,
            const.GENERIC_TYPE_SENSOR_MULTILEVEL,
            const.GENERIC_TYPE_SWITCH_MULTILEVEL,
            const.GENERIC_TYPE_SENSOR_NOTIFICATION,
            const.GENERIC_TYPE_GENERIC_CONTROLLER,
            const.GENERIC_TYPE_SWITCH_REMOTE,
            const.GENERIC_TYPE_REPEATER_SLAVE,
            const.GENERIC_TYPE_THERMOSTAT,
            const.GENERIC_TYPE_WALL_CONTROLLER,
        ],
        const.DISC_VALUES: dict(
            DEFAULT_VALUES_SCHEMA,
            **{
                const.DISC_PRIMARY: {
                    const.DISC_COMMAND_CLASS: [const.COMMAND_CLASS_SWITCH_BINARY],
                    const.DISC_TYPE: const.TYPE_BOOL,
                    const.DISC_GENRE: const.GENRE_USER,
                }
            },
        ),
    },
]


def check_node_schema(node, schema):
    """Check if node matches the passed node schema."""
    if const.DISC_NODE_ID in schema and node.node_id not in schema[const.DISC_NODE_ID]:
        _LOGGER.debug(
            "node.node_id %s not in node_id %s",
            node.node_id,
            schema[const.DISC_NODE_ID],
        )
        return False
    if (
        const.DISC_GENERIC_DEVICE_CLASS in schema
        and node.node_generic not in schema[const.DISC_GENERIC_DEVICE_CLASS]
    ):
        _LOGGER.debug(
            "node.node_generic %s not in generic_device_class %s",
            node.node_generic,
            schema[const.DISC_GENERIC_DEVICE_CLASS],
        )
        return False
    if (
        const.DISC_SPECIFIC_DEVICE_CLASS in schema
        and node.node_specific not in schema[const.DISC_SPECIFIC_DEVICE_CLASS]
    ):
        _LOGGER.debug(
            "node.node_specific %s not in specific_device_class %s",
            node.node_specific,
            schema[const.DISC_SPECIFIC_DEVICE_CLASS],
        )
        return False
    return True


def check_value_schema(value, schema):
    """Check if the value matches the passed value schema."""
    if (
        const.DISC_COMMAND_CLASS in schema
        and value.parent.command_class_id not in schema[const.DISC_COMMAND_CLASS]
    ):
        _LOGGER.debug(
            "value.parent.command_class_id %s not in command_class %s",
            value.parent.command_class_id,
            schema[const.DISC_COMMAND_CLASS],
        )
        return False
    if const.DISC_TYPE in schema and value.type not in schema[const.DISC_TYPE]:
        _LOGGER.debug(
            "value.type %s not in type %s", value.type, schema[const.DISC_TYPE]
        )
        return False
    if const.DISC_GENRE in schema and value.genre not in schema[const.DISC_GENRE]:
        _LOGGER.debug(
            "value.genre %s not in genre %s", value.genre, schema[const.DISC_GENRE]
        )
        return False
    if const.DISC_INDEX in schema and value.index not in schema[const.DISC_INDEX]:
        _LOGGER.debug(
            "value.index %s not in index %s", value.index, schema[const.DISC_INDEX]
        )
        return False
    if (
        const.DISC_INSTANCE in schema
        and value.instance not in schema[const.DISC_INSTANCE]
    ):
        _LOGGER.debug(
            "value.instance %s not in instance %s",
            value.instance,
            schema[const.DISC_INSTANCE],
        )
        return False
    if const.DISC_SCHEMAS in schema:
        found = False
        for schema_item in schema[const.DISC_SCHEMAS]:
            found = found or check_value_schema(value, schema_item)
        if not found:
            return False

    return True
