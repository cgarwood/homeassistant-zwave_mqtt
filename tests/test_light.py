"""Test Z-Wave Lights."""
from custom_components.zwave_mqtt.light import byte_to_zwave_brightness

from tests.common import setup_zwave


async def test_light(hass, sent_messages):
    """Test setting up config entry."""
    await setup_zwave(hass, "generic_network_dump.csv")

    # Test loaded
    state = hass.states.get("light.aeotec_limited_zwa002_led_bulb_6_multi_color_level")
    assert state is not None
    assert state.state == "off"

    # Test turning on
    new_brightness = 45
    await hass.services.async_call(
        "light",
        "turn_on",
        {
            "entity_id": "light.aeotec_limited_zwa002_led_bulb_6_multi_color_level",
            "brightness": new_brightness,
        },
        blocking=True,
    )
    assert len(sent_messages) == 2  # seting brightness involves 2 calls (duration)
    msg = sent_messages[1]
    assert msg["topic"] == "OpenZWave/1/command/setvalue/"
    assert msg["payload"] == {
        "Value": byte_to_zwave_brightness(new_brightness),
        "ValueIDKey": 659128337,
    }

    # Test turning off
    await hass.services.async_call(
        "light",
        "turn_off",
        {"entity_id": "light.aeotec_limited_zwa002_led_bulb_6_multi_color_level"},
        blocking=True,
    )
    assert len(sent_messages) == 4
    msg = sent_messages[3]
    assert msg["topic"] == "OpenZWave/1/command/setvalue/"
    assert msg["payload"] == {"Value": 0, "ValueIDKey": 659128337}
