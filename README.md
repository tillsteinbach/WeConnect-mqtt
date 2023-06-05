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
If you want to integrate data from your weconnect enabled car a standard protocol such as [MQTT](https://mqtt.org) can be very helpful. This Client enables you to integrate with the [MQTT Broker](https://mqtt.org/software/) of your choice (e.g. your home automation solution such as [ioBroker](https://www.iobroker.net), [FHEM](https://fhem.de) or [Home Assistant](https://www.home-assistant.io))

## Requirements
You need to install python 3 on your system: [How to install python](https://realpython.com/installing-python/). The minimum required python version is 3.8

### Login & Consent
WeConnect-mqtt is based on the new WeConnect ID API that was introduced with the new series of ID cars. If you use another car or hybrid you probably need to agree to the terms and conditions of the WeConnect ID interface. Easiest to do so is by installing the WeConnect ID app on your smartphone and login there. If necessary you will be asked to agree to the terms and conditions.

## How to install
If you want to use WeConnect-mqtt, the easiest way is to obtain it from [PyPI](https://pypi.org/project/weconnect-mqtt/). Just install instead using:
```bash
pip3 install weconnect-mqtt
```
### Updates
If you want to update WeConnect-mqtt, the easiest way is:
```bash
pip3 install weconnect-mqtt --upgrade
```
### Docker
There is also a Docker image to easily host WeConnect-MQTT: [See on Dockerhub](https://hub.docker.com/r/tillsteinbach/weconnect-mqtt)

## How to use
Start weconnect-mqtt from the commandline:
```bash
weconnect-mqtt
```
You get all the usage information by using the --help command
```bash
weconnect-mqtt --help
```
An example to connect with an MQTT broker at 192.168.0.1 with user test and password test123 is
```bash
weconnect-mqtt --username test@test.de --password test123 --mqttbroker 192.168.0.1 --mqtt-username test --mqtt-password test123 --prefix weconnect
```
The client uses user test@test.de and password test123 in this example to connect to weconnect

### S-PIN
For some commands (e.g. locking/unlocking supported on some cars) you need in addition to your login the so called S-PIN, you can provide it with the `--spin` option:
```bash
weconnect-mqtt --username test@test.de --password test123  --spin 1234 --mqttbroker 192.168.0.1 --mqtt-username test --mqtt-password test123 --prefix weconnect
```

### Credentials
If you do not want to provide your username or password all the time you have to create a ".netrc" file at the appropriate location (usually this is your home folder):
```
# For WeConnect
machine volkswagen.de
login test@test.de
password testpassword123

# For the MQTTBroker
machine 192.168.0.1
login test
password testpassword123
```
You can also provide the location of the netrc file using the --netrc option

The optional S-PIN needed for some commands can be provided in the account section:
```
# For WeConnect
machine volkswagen.de
login test@test.de
password testpassword123
account 1234
```

### Charging stations
You can also obtain data from charging stations by adding a location with e.g. `--chargingLocation 52.437132 10.796628` and a radius in meters with `--chargingLocationRadius=500`.
Data for charging stations is mostly static, but you can see the current availability.

### Topics
If your broker does not let you observe all available topics you can pass the parameter `--list-topics` to get all topics displayed on the commandline. Topics marked as "(writeable)" can be manipulated.
There are also two topics to receive all available topics as a comma seperated list: `weconnect/0/mqtt/topics` lists all available topics, `weconnect/0/mqtt/writeableTopics` provides topics that can be manipulated.

### Disabling features
You can disable data for the cars capabilities with `--no-capabilities`
If you only need a subset of the data you can use the `--selective` option. E.g. `--selective climatisation`

### Images
You can enable ASCII Art pictures of the cars with `--pictures`

#### PNG vehicle images
If your client can deal with PNG-images received through MQTT you can set `--picture-format png`

### Times
By default the times coming from the car are UTC isoformat. You can convert times to your local timezone by adding `--convert-times`. Convert times will use the systems timezone. If you want to set a specific timezone use e.g. `--convert-times Europe/Berlin`.
You can format times in your local format by adding `--timeformat`. This will use the default Date/Time format of your locale setting. If you want to set a specific format use e.g. `--timeformat '%a %d %b %Y %T'`.
If you want to set the date in another language than default on your system use e.g. `--locale de_DE`.

### Raw JSON
If you want to continue working with the whole data you can also enable the topic `weconnect/0/rawjson` by adding `--with-raw-json-topic`. The topic is published on every change of the json string.

## Tested with
- Volkswagen ID.3 Modelyear 2021
- Volkswagen Passat GTE Modelyear 2021

## Reporting Issues
Please feel free to open an issue at [GitHub Issue page](https://github.com/tillsteinbach/WeConnect-mqtt/issues) to report problems you found.

## More Questions?
Please see the wiki [Wiki](https://github.com/tillsteinbach/WeConnect-mqtt/wiki) or start a [discussion](https://github.com/tillsteinbach/WeConnect-mqtt/discussions).

### Known Issues
- The Tool is in alpha state and may change unexpectedly at any time!

## Related Projects:
- [WeConnect-cli](https://github.com/tillsteinbach/WeConnect-cli): Commandline Interface to interact with the Volkswagen WeConnect Services
- [WeConnect-python](https://github.com/tillsteinbach/WeConnect-python): Python API to connect to Volkswagen WeConnect Services
- [VWsFriend](https://github.com/tillsteinbach/VWsFriend): VWsFriend is a software to visualize and record statistics of your car and allows control via HomeKit

## Seat, Cupra, Skoda IV, ...
In an effort to try to make WeConnect-MQTT also to work with latest generation of vehicles from other volkswagen brands I'm looking for users to temporarily share access to their accounts. If you are willing to support please send me a message.
- Already tried: Cupra Born (The API looks a bit different, maybe it is older, I will check again in some weeks), thanks to the user initdebugs
