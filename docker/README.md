# WeConnect-MQTT
[![GitHub sourcecode](https://img.shields.io/badge/Source-GitHub-green)](https://github.com/tillsteinbach/WeConnect-mqtt/)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/tillsteinbach/WeConnect-mqtt)](https://github.com/tillsteinbach/WeConnect-mqtt/releases/latest)
[![GitHub](https://img.shields.io/github/license/tillsteinbach/WeConnect-mqtt)](https://github.com/tillsteinbach/WeConnect-mqtt/blob/master/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/tillsteinbach/WeConnect-mqtt)](https://github.com/tillsteinbach/WeConnect-mqtt/issues)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/weconnect-mqtt?label=PyPI%20Downloads)](https://pypi.org/project/weconnect-mqtt/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/weconnect-mqtt)](https://pypi.org/project/weconnect-mqtt/)
[![Docker Image Size (latest semver)](https://img.shields.io/docker/image-size/tillsteinbach/weconnect-mqtt?sort=semver)](https://hub.docker.com/r/tillsteinbach/weconnect-mqtt)
[![Docker Pulls](https://img.shields.io/docker/pulls/tillsteinbach/weconnect-mqtt)](https://hub.docker.com/r/tillsteinbach/weconnect-mqtt)
[![Donate at PayPal](https://img.shields.io/badge/Donate-PayPal-2997d8)](https://www.paypal.com/donate?hosted_button_id=2BVFF5GJ9SXAJ)
[![Sponsor at Github](https://img.shields.io/badge/Sponsor-GitHub-28a745)](https://github.com/sponsors/tillsteinbach)

[MQTT](https://mqtt.org) Client that publishes data from Volkswagen WeConnect Services


## What is the purpose?
If you want to integrate data from your WeConnect enabled car a standard protocol such as [MQTT](https://mqtt.org) can be very helpful. This Client enables you to integrate with the [MQTT Broker](https://mqtt.org/software/) of your choice (e.g. your home automation solution such as [ioBroker](https://www.iobroker.net), [FHEM](https://fhem.de) or [Home Assistant](https://www.home-assistant.io))

## How to install
### Using docker-compose
When using docker-compose configure WeConnect-MQTT like that:
```yml
version: '3.3'

services:
  weconnect-mqtt:
    image: "tillsteinbach/weconnect-mqtt:latest"
    restart: unless-stopped
    environment:
      - USER=my@vwid-user.de
      - PASSWORD=myvwidpassword
      - BROKER_ADDRESS=192.168.0.1
      - ADDITIONAL_PARAMETERS=--mqtt-username test --mqtt-password test
```

### Without Docker
If you don't want to use docker you can obtain weconnect-mqtt also as a stand-alone application from [PyPI](https://pypi.org/project/weconnect-mqtt/). Just install instead using:
```bash
pip install weconnect-mqtt
```

## Tested with
- Volkswagen ID.3 Modelyear 2021
- Volkswagen Passat GTE Modelyear 2021

## Reporting Issues
Please feel free to open an issue at [GitHub Issue page](https://github.com/tillsteinbach/WeConnect-mqtt/issues) to report problems you found.

### Known Issues
- The Tool is in alpha state and may change unexpectedly at any time!

## Related Projects:
- [WeConnect-cli](https://github.com/tillsteinbach/WeConnect-cli): Commandline Interface to interact with the Volkswagen WeConnect Services
- [WeConnect-python](https://github.com/tillsteinbach/WeConnect-python): Python API to connect to Volkswagen WeConnect Services
