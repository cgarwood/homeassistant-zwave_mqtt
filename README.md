# Home Assistant Z-Wave over MQTT Integration (Pre-Release)
This integration allows you to utilize OpenZWave's qt-openzwave to control a Z-Wave network over MQTT.

**This is an early beta/pre-release and there are still significant limitations**

## Requirements
- You must have an MQTT server running and the MQTT integration set up in Home Assistant
- See https://github.com/OpenZWave/qt-openzwave/blob/mqtt/docs/MQTT.md for instructions on downloading and configuring the OpenZWave MQTT daemon

## Limitations
- Currently only supports binary_sensor, sensor, and switch platforms

## Upstream Resources Used
- [python-openzwave-mqtt](https://github.com/cgarwood/python-openzwave-mqtt) - Converts qt-openzwave MQTT messages to Python objects and events
- [qt-openzwave](https://github.com/OpenZWave/qt-openzwave/tree/mqtt) - OpenZWave MQTT Daemon