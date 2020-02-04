# Home Assistant Z-Wave over MQTT Integration (Pre-Release)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

This integration allows you to utilize OpenZWave's qt-openzwave to control a Z-Wave network over MQTT. It is currently available as a custom component through HACS and will be submitted as an official Home Assistant component once it has matured a bit.

**This is an early beta/pre-release and there are still significant limitations**

## Requirements

- MQTT server and the MQTT integration set up in Home Assistant
- QT-OpenZwave daemon (https://github.com/OpenZWave/qt-openzwave)
- Supported Z-wave dongle compatible with OpenZWave 1.6 ([list](https://www.home-assistant.io/docs/z-wave/controllers/#supported-z-wave-usb-sticks--hardware-modules))

## Quick start
- Remove the normal Z-Wave integration from your setup (if present).
- Install the Mosquittto broker addon and configure MQTT in HomeAssistant integrations page.
- Make sure you have HACS set-up (https://github.com/custom-components/hacs).
- Install custom add-on repository to get the OpenZWave daemon: https://github.com/marcelveldt/hassio-addons-repo
- Install the OpenZWave Daemon add-on repository, configure and start.
- Carefully check the logs of the daemon if it started successfully!
- Go to the HomeAssistant integrations page, add Zwave MQTT integration.


## Features and Limitations
- Currently already supports binary_sensor, sensor, and switch platforms
- Scenes support for both Central scenes and node/network scenes:
    Will fire HomeAssistant event zwave_mqtt.scene_activated.
- Light support is currently limited to dimmers only, RGB bulbs are not yet implemented.
- Other platforms will be added soon!

## Contributing
Contributions are welcome! If you'd like to contribute, feel free to pick up anything on the current [GitHub issues](https://github.com/cgarwood/homeassistant-zwave_mqtt/issues) list!

### Code Formatting
We try to follow the core Home Assistant style guidelines. Code should be formatted with `black` and imports sorted with `isort`. We have pre-commit hooks to help automate this process. Run `pip install pre-commit` and then `pre-commit install` to install the pre-commit hooks for code formatting.

## Upstream Resources Used
- [python-openzwave-mqtt](https://github.com/cgarwood/python-openzwave-mqtt) - Converts qt-openzwave MQTT messages to Python objects and events
- [qt-openzwave](https://github.com/OpenZWave/qt-openzwave) - OpenZWave MQTT Daemon
