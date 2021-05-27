from datetime import datetime
from enum import Enum
import sys
import argparse
import netrc
import getpass
import logging
import time

import paho.mqtt.client

from weconnect import weconnect, addressable

from .__version import __version__

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
DEFAULT_LOG_LEVEL = "ERROR"

LOG = logging.getLogger("weconnect-mqtt")


class NumberRangeArgument:

    def __init__(self, imin=None, imax=None):
        self.imin = imin
        self.imax = imax

    def __call__(self, arg):
        try:
            value = int(arg)
        except ValueError as e:
            raise self.exception() from e
        if (self.imin is not None and value < self.imin) or (self.imax is not None and value > self.imax):
            raise self.exception()
        return value

    def exception(self):
        if self.imin is not None and self.imax is not None:
            return argparse.ArgumentTypeError(f'Must be a number from {self.imin} to {self.imax}')
        if self.imin is not None:
            return argparse.ArgumentTypeError(f'Must be a number not smaller than {self.imin}')
        if self.imax is not None:
            return argparse.ArgumentTypeError(f'Must be number not larger than {self.imax}')

        return argparse.ArgumentTypeError('Must be a number')


def main():  # noqa: C901
    parser = argparse.ArgumentParser(
        prog='weconnect-mqtt',
        description='Commandline Interface to interact with the Volkswagen WeConnect Services')
    parser.add_argument('--version', action='version',
                        version='%(prog)s {version}'.format(version=__version__))
    parser.add_argument('--mqttbroker', type=str, help='Address of MQTT Broker to connect to', required=True)
    parser.add_argument('--mqttport', type=str, help='Port of MQTT Broker to connect to', required=False, default=1883)
    parser.add_argument('-mu', '--mqtt-username', type=str, dest='mqttusername',
                        help='Username for MQTT broker', required=False)
    parser.add_argument('-mp', '--mqtt-password', type=str, dest='mqttpassword',
                        help='Password for MQTT broker', required=False)
    parser.add_argument('-u', '--username', type=str, help='Username of Volkswagen id', required=False)
    parser.add_argument('-p', '--password', type=str, help='Password of Volkswagen id', required=False)
    parser.add_argument('--netrc', type=str, help='File in netrc syntax providing login, default is the default netrc '
                        'location (usually your users folder). Netrc is only used when username and password are not '
                        'provided as arguments', default=None, required=False)
    parser.add_argument('-i', '--interval', help='Query interval in seconds',
                              type=NumberRangeArgument(300, 3500), required=False, default=300)
    parser.add_argument('--prefix', help='MQTT topic prefix',
                        type=str, required=False, default='weconnect/0')
    parser.add_argument('-v', '--verbose', action="append_const", const=-1,)

    args = parser.parse_args()

    username = None
    password = None

    if args.username is not None and args.password is not None:
        username = args.username
        password = args.password
    else:
        try:
            secrets = netrc.netrc(file=args.netrc)
            username, _, password = secrets.authenticators("volkswagen.de")
        except FileNotFoundError:
            if not args.username:
                LOG.error('.netrc file was not found. Create it or provide at least a username with --username')
                sys.exit(1)
            username = args.username
            password = getpass.getpass()

    mqttusername = None
    mqttpassword = None
    if args.mqttusername is not None:
        mqttusername = args.mqttusername
    if args.mqttpassword is not None:
        mqttpassword = args.mqttpassword

    if mqttusername is None and mqttpassword is None:
        try:
            secrets = netrc.netrc(file=args.netrc)
            authenticator = secrets.authenticators(args.mqttbroker)
            if authenticator is not None:
                mqttusername, _, mqttpassword = authenticator
        except FileNotFoundError:
            if args.netrc is not None:
                LOG.error('Provided .netrc file was not found.')
                sys.exit(1)

    logging.basicConfig(level=logging.INFO)

    mqttCLient = WeConnectMQTTClient(interval=args.interval, prefix=args.prefix)

    if mqttusername is not None:
        mqttCLient.username_pw_set(username=mqttusername, password=mqttpassword)

    mqttCLient.connectWeConnect(username=username, password=password)
    mqttCLient.connect(args.mqttbroker, args.mqttport, 60)
    # blocking run
    mqttCLient.run()
    mqttCLient.disconnect()
    mqttCLient.weConnect.persistTokens()


class WeConnectMQTTClient(paho.mqtt.client.Client):
    def __init__(self, interval, prefix='weconnect/0'):
        super().__init__()
        self.weConnect = None
        self.prefix = prefix
        self.interval = interval

    def disconnect(self, reasoncode=None, properties=None):
        self.publish(topic=f'{self.prefix}/mqtt/weconnectConnected', payload=False)
        super().disconnect(reasoncode, properties)

    def connectWeConnect(self, username, password):
        LOG.info('Connect to WeConnect')
        self.weConnect = weconnect.WeConnect(username=username, password=password, updateAfterLogin=False)
        self.weConnect.addObserver(self.onWeConnectEvent, addressable.AddressableLeaf.ObserverEvent.VALUE_CHANGED)

    def updateWeConnect(self):
        LOG.info('Update data from WeConnect')
        self.weConnect.update()
        self.publish(topic=f'{self.prefix}/mqtt/weconnectUpdated', payload=str(datetime.now()))

    def onWeConnectEvent(self, element, flags):
        if flags & addressable.AddressableLeaf.ObserverEvent.VALUE_CHANGED:
            if isinstance(element.value, (str, int, float)) or element.value is None:
                convertedValue = element.value
            elif isinstance(element.value, Enum):
                convertedValue = element.value.value
            else:
                convertedValue = str(element.value)

            self.publish(topic=f'{self.prefix}{element.getGlobalAddress()}', payload=convertedValue)

    def on_connect(self, mqttc, obj, flags, rc):  # pylint: disable=W0221,W0236,W0613
        if rc == 0:
            LOG.info('Connected to MQTT broker')
            self.publish(topic=f'{self.prefix}/mqtt/weconnectForceUpdate', payload=False)
            self.subscribe(f'{self.prefix}/mqtt/weconnectForceUpdate')

            self.publish(topic=f'{self.prefix}/mqtt/weconnectUpdateInterval_s', payload=self.interval)
            self.subscribe(f'{self.prefix}/mqtt/weconnectUpdateInterval_s')

            self.publish(topic=f'{self.prefix}/mqtt/weconnectConnected', payload=True)

            self.updateWeConnect()
        elif rc == 1:
            LOG.error('Could not connect (%d): incorrect protocol version', rc)
        elif rc == 2:
            LOG.error('Could not connect (%d): invalid client identifier', rc)
        elif rc == 3:
            LOG.error('Could not connect (%d): server unavailable. Retrying in 10 seconds', rc)
            time.sleep(10)
            self.reconnect()
        elif rc == 4:
            LOG.error('Could not connect (%d): bad username or password', rc)
        elif rc == 5:
            LOG.error('Could not connect (%d): not authorised', rc)
        else:
            print('Could not connect: %d', rc, file=sys.stderr)
            sys.exit(1)

    def on_message(self, mqttc, obj, msg):  # pylint: disable=W0221,W0236,W0613
        if msg.topic == f'{self.prefix}/mqtt/weconnectForceUpdate':
            if msg.payload.lower() == b'True'.lower():
                LOG.info('Update triggered by MQTT message')
                self.updateWeConnect()
                self.publish(topic=f'{self.prefix}/mqtt/weconnectForceUpdate', payload=False)
        elif msg.topic == f'{self.prefix}/mqtt/weconnectUpdateInterval_s':
            if str(msg.payload.decode()).isnumeric():
                newInterval = int(msg.payload)
                if newInterval < 300:
                    LOG.error('New intervall of %ss by MQTT message is too low. Minimum is 300s', msg.payload.decode())
                    self.publish(topic=f'{self.prefix}/mqtt/weconnectUpdateInterval_s', payload=self.interval)
                elif newInterval > 3500:
                    LOG.error('New intervall of %ss by MQTT message is too large. Maximum is 3500s',
                              msg.payload.decode())
                    self.publish(topic=f'{self.prefix}/mqtt/weconnectUpdateInterval_s', payload=self.interval)
                else:
                    self.interval = newInterval
                    LOG.info('New intervall set to %ds by MQTT message', self.interval)
            else:
                LOG.error('MQTT message for new interval does not contain a number: %s', msg.payload.decode())
        else:
            LOG.error('I don\'t understand message %s: %s', msg.topic, msg.payload)

    def run(self):
        self.loop_start()
        try:
            while True:
                time.sleep(self.interval)
                self.updateWeConnect()
        except KeyboardInterrupt:
            self.loop_stop(force=False)
