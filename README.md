# Home Assistant Z-Wave over MQTT Integration (Pre-Release)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

This integration allows you to utilize OpenZWave's qt-openzwave to control a Z-Wave network over MQTT. It is currently available as a custom component through HACS and will be submitted as an official Home Assistant component once it has matured a bit.

**This is an early beta/pre-release and there are still significant limitations**

## Requirements
- You must have an MQTT server running and the MQTT integration set up in Home Assistant
- See https://github.com/OpenZWave/qt-openzwave/blob/mqtt/docs/MQTT.md for instructions on downloading and configuring the OpenZWave MQTT daemon

## Limitations
- Currently only supports binary_sensor, sensor, and switch platforms

## Contributing
Contributions are welcome! If you'd like to contribute, feel free to pick up anything on the current [GitHub issues](https://github.com/cgarwood/homeassistant-zwave_mqtt/issues) list!

## Upstream Resources Used
- [python-openzwave-mqtt](https://github.com/cgarwood/python-openzwave-mqtt) - Converts qt-openzwave MQTT messages to Python objects and events
- [qt-openzwave](https://github.com/OpenZWave/qt-openzwave/tree/mqtt) - OpenZWave MQTT Daemon