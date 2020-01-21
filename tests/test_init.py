"""Test integration initialization."""

from custom_components.zwave_mqtt import DOMAIN, PLATFORMS

from tests.common import setup_zwave


async def test_init_entry(hass):
    """Test setting up config entry."""
    await setup_zwave(hass)

    # Verify everything loaded.
    assert "zwave_mqtt" in hass.config.components
    for platform in PLATFORMS:
        assert platform in hass.config.components, platform
        assert f"{platform}.{DOMAIN}" in hass.config.components, f"{platform}.{DOMAIN}"
