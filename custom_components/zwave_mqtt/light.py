"""Support for Z-Wave lights."""
import logging

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_HS_COLOR,
    ATTR_TRANSITION,
    ATTR_WHITE_VALUE,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR,
    SUPPORT_TRANSITION,
    SUPPORT_WHITE_VALUE,
    Light,
)
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
import homeassistant.util.color as color_util

from .const import DOMAIN
from .entity import ZWaveDeviceEntity

_LOGGER = logging.getLogger(__name__)

COLOR_CHANNEL_WARM_WHITE = 0x01
COLOR_CHANNEL_COLD_WHITE = 0x02
COLOR_CHANNEL_RED = 0x04
COLOR_CHANNEL_GREEN = 0x08
COLOR_CHANNEL_BLUE = 0x10


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Z-Wave Light from Config Entry."""

    @callback
    def async_add_light(values):
        """Add Z-Wave Light."""
        _LOGGER.warning("Light add light entity: values: %s", values._values)
        if values.color:
            light = ZwaveColorLight(values)
        else:
            light = ZwaveDimmer(values)
        async_add_entities([light])

    async_dispatcher_connect(hass, "zwave_new_light", async_add_light)

    await hass.data[DOMAIN][config_entry.entry_id]["mark_platform_loaded"]("light")


def byte_to_zwave_brightness(value):
    """Convert brightness in 0-255 scale to 0-99 scale.

    `value` -- (int) Brightness byte value from 0-255.
    """
    if value > 0:
        return max(1, int((value / 255) * 99))
    return 0


class ZwaveDimmer(ZWaveDeviceEntity, Light):
    """Representation of a Z-Wave dimmer."""

    def __init__(self, values):
        """Initialize the light."""
        ZWaveDeviceEntity.__init__(self, values)
        self._supported_features = None
        self.value_added()

    @callback
    def value_added(self):
        """Call when a new value is added to this entity."""
        self._supported_features = SUPPORT_BRIGHTNESS
        if self.values.dimming_duration is not None:
            self._supported_features |= SUPPORT_TRANSITION
        _LOGGER.warning("Light value added: values: %s", self.values._values)

    @property
    def brightness(self):
        """Return the brightness of this light between 0..255."""
        if "target" in self.values:
            return round((self.values.target.value / 99) * 255)
        return round((self.values.primary.value / 99) * 255)

    @property
    def is_on(self):
        """Return true if device is on (brightness above 0)."""
        if "target" in self.values:
            return self.values.target.value > 0
        return self.values.primary.value > 0

    @property
    def supported_features(self):
        """Flag supported features."""
        return self._supported_features

    async def async_set_duration(self, **kwargs):
        """Set the transition time for the brightness value.

        Zwave Dimming Duration values:
        0       = instant
        0-127   = 1 second to 127 seconds
        128-254 = 1 minute to 127 minutes
        255     = factory default
        """
        if self.values.dimming_duration is None:
            if ATTR_TRANSITION in kwargs:
                _LOGGER.debug("Dimming not supported by %s.", self.entity_id)
            return

        if ATTR_TRANSITION not in kwargs:
            # no transition specified by user, use defaults
            new_value = 255
        else:
            # transition specified by user, convert to zwave value
            transition = kwargs[ATTR_TRANSITION]
            if transition <= 127:
                new_value = int(transition)
            elif transition > 7620:
                new_value = 254
                _LOGGER.warning(
                    "Transition clipped to 127 minutes for %s.", self.entity_id
                )
            else:
                minutes = int(transition / 60)
                _LOGGER.debug(
                    "Transition rounded to %d minutes for %s.", minutes, self.entity_id
                )
                new_value = minutes + 128

        # only send value if it differs from current
        # this prevents a command for nothing
        if self.values.dimming_duration.value != new_value:
            self.values.dimming_duration.send_value(new_value)

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self.async_set_duration(**kwargs)

        # Zwave multilevel switches use a range of [0, 99] to control
        # brightness. Level 255 means to set it to previous value.
        if ATTR_BRIGHTNESS in kwargs:
            brightness = kwargs[ATTR_BRIGHTNESS]
            brightness = byte_to_zwave_brightness(brightness)
        else:
            brightness = 255

        self.values.primary.send_value(brightness)

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        await self.async_set_duration(**kwargs)

        self.values.primary.send_value(0)


class ZwaveColorLight(ZwaveDimmer):
    """Representation of a Z-Wave color changing light."""

    @callback
    def value_added(self):
        """Call when a new value is added to this entity."""
        super().value_added()

        # If no rgb channels supported, color is not supported.
        if None in (self.values.color_channels, self.values.color_channels.value,):
            return

        if self.values.color_channels.value & (
            COLOR_CHANNEL_WARM_WHITE | COLOR_CHANNEL_COLD_WHITE
        ):
            self._supported_features |= SUPPORT_WHITE_VALUE

        if not (
            self.values.color_channels.value & COLOR_CHANNEL_RED
            or self.values.color_channels.value & COLOR_CHANNEL_GREEN
            or self.values.color_channels.value & COLOR_CHANNEL_BLUE
        ):
            return

        self._supported_features |= SUPPORT_COLOR

    @property
    def hs_color(self):
        """Return the hs color."""
        # Color Data String
        color = self.values.color.value

        # RGB is always present in the openzwave color data string.
        rgb = [int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)]
        hs_color = color_util.color_RGB_to_hs(*rgb)
        return hs_color

    @property
    def white_value(self):
        """Return the white value of this light between 0..255."""
        # Color Data String
        color = self.values.color.value
        # Color channel
        color_channel = self.values.color_channel.value
        # Parse remaining color channels. Openzwave appends white channels
        # that are present.
        index = 7
        # Warm white
        if color_channel & COLOR_CHANNEL_WARM_WHITE:
            warm_white = int(color[index : index + 2], 16)
            index += 2
        else:
            warm_white = 0

        # Cold white
        if color_channel & COLOR_CHANNEL_COLD_WHITE:
            cold_white = int(color[index : index + 2], 16)
        else:
            cold_white = 0

        if color_channel & COLOR_CHANNEL_WARM_WHITE:
            white = warm_white

        elif color_channel & COLOR_CHANNEL_COLD_WHITE:
            white = cold_white

        return white

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        rgbw = None
        color = self.values.color.value
        hs_color = kwargs.get(ATTR_HS_COLOR)
        white = kwargs.get(ATTR_WHITE_VALUE)
        if hs_color is not None and white is None:
            # white LED must be off in order for color to work
            white = 0

        if (white or hs_color) and color is not None:
            rgbw = "#"
            hs_color = hs_color or (0, 0)
            for colorval in color_util.color_hs_to_RGB(*hs_color):
                rgbw += format(colorval, "02x")
            if white is not None:
                rgbw += format(white, "02x") + "00"
            else:
                rgbw += "0000"

        if rgbw and self.values.color:
            self.values.color.send_value(rgbw)

        await super().async_turn_on(**kwargs)
