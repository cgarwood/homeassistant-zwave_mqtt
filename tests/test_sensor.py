"""Test Z-Wave Sensors."""
from tests.common import setup_zwave


async def test_sensor(hass, sent_messages):
    """Test setting up config entry."""
    await setup_zwave(hass, "generic_network_dump.csv")

    # Test standard sensor
    state = hass.states.get("sensor.smart_plug_electric_v")
    assert state is not None
    assert state.state == "123.9"
    assert state.attributes["unit_of_measurement"] == "V"
