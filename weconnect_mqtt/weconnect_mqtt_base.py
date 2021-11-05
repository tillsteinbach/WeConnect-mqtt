from datetime import datetime, timedelta, timezone
from enum import Enum
import os
import sys
import socket
import argparse
import netrc
import getpass
import logging
import time
import ssl

import paho.mqtt.client
from PIL import Image
import ascii_magic

from weconnect import weconnect, addressable, errors, util
from weconnect.__version import __version__ as __weconnect_version__

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


def main():  # noqa: C901  # pylint: disable=too-many-branches,too-many-statements
    parser = argparse.ArgumentParser(
        prog='weconnect-mqtt',
        description='Commandline Interface to interact with the Volkswagen WeConnect Services')
    parser.add_argument('--version', action='version',
                        version=f'%(prog)s {__version__} (using WeConnect-python {__weconnect_version__})')
    parser.add_argument('--mqttbroker', type=str, help='Address of MQTT Broker to connect to', required=True)
    parser.add_argument('--mqttport', type=NumberRangeArgument(1, 65535), help='Port of MQTT Broker. Default is 1883 (8883 for TLS)',
                        required=False, default=None)
    parser.add_argument('--mqttclientid', required=False, default=None, help='Id of the client. Default is a random id')
    parser.add_argument('-k', '--mqttkeepalive', required=False, type=int, default=60,
                        help='Time between keep-alive messages')
    parser.add_argument('-mu', '--mqtt-username', type=str, dest='mqttusername',
                        help='Username for MQTT broker', required=False)
    parser.add_argument('-mp', '--mqtt-password', type=str, dest='mqttpassword',
                        help='Password for MQTT broker', required=False)
    parser.add_argument('--transport', required=False, default='tcp', choices=["tcp", 'websockets'],
                        help='EXPERIMENTAL support for websockets transport')
    parser.add_argument('-s', '--use-tls', action='store_true', help='EXPERIMENTAL')
    parser.add_argument('--insecure', action='store_true', help='EXPERIMENTAL')
    parser.add_argument('--cacerts', required=False, default=None, help='EXPERIMENTAL path to the Certificate Authority'
                        ' certificate files that are to be treated as trusted by this client')
    parser.add_argument('--cert', required=False, default=None, help='EXPERIMENTAL PEM encoded client certificate')
    parser.add_argument('--key', required=False, default=None, help='EXPERIMENTAL PEM encoded client private key')
    parser.add_argument('--tls-version', required=False, default=None, choices=['tlsv1.2', 'tlsv1.1', 'tlsv1'],
                        help='EXPERIMENTAL TLS protocol version')

    parser.add_argument('-u', '--username', type=str, help='Username of Volkswagen id', required=False)
    parser.add_argument('-p', '--password', type=str, help='Password of Volkswagen id', required=False)
    defaultNetRc = os.path.join(os.path.expanduser("~"), ".netrc")
    parser.add_argument('--netrc', help=f'File in netrc syntax providing login (default: {defaultNetRc}).'
                        ' Netrc is only used when username and password are not provided  as arguments',
                        default=None, required=False)
    parser.add_argument('-i', '--interval', help='Query interval in seconds',
                              type=NumberRangeArgument(300, 3500), required=False, default=300)
    parser.add_argument('--picture-cache-interval', dest='pictureCache', help='Picture download interval in seconds, this does not influence the interval in'
                        ' which the status picture is updated', type=NumberRangeArgument(1), required=False, default=86400)
    parser.add_argument('--prefix', help='MQTT topic prefix',
                        type=str, required=False, default='weconnect/0')
    parser.add_argument('--ignore-for', dest='ignore', help='Ignore messages for first IGNORE seconds after subscribe to aviod '
                        'retained messages from the broker to make changes to the car (default is 5s) if you don\'t want this behavious set to 0',
                        type=int, required=False, default=5)
    parser.add_argument('-v', '--verbose', action="append_const", const=-1,)
    parser.add_argument('-l', '--chargingLocation', nargs=2, metavar=('latitude', 'longitude'), type=float,
                        help='If set charging locations will be added to the result around the given coordinates')
    parser.add_argument('--chargingLocationRadius', type=NumberRangeArgument(0, 100000),
                        help='Radius in meters around the chargingLocation to search for chargers')
    parser.add_argument('--no-capabilities', dest='noCapabilities', help='Do not add capabilities', action='store_true')
    parser.add_argument('--pictures', help='Add ASCII art pictures', action='store_true')

    args = parser.parse_args()

    logLevel = LOG_LEVELS.index(DEFAULT_LOG_LEVEL)
    for adjustment in args.verbose or ():
        logLevel = min(len(LOG_LEVELS) - 1, max(logLevel + adjustment, 0))

    logging.basicConfig(level=LOG_LEVELS[logLevel])
    LOG.info('WeConnect-mqtt %s (using WeConnect-python %s)', __version__, __weconnect_version__)

    usetls = args.use_tls
    if args.cacerts:
        usetls = True

    if args.mqttport is None:
        if usetls:
            args.mqttport = 8883
        else:
            args.mqttport = 1883

    username = None
    password = None

    if args.username is not None and args.password is not None:
        username = args.username
        password = args.password
    else:
        if args.netrc is not None:
            netRcFilename = args.netrc
        else:
            netRcFilename = defaultNetRc
        try:
            secrets = netrc.netrc(file=args.netrc)
            secret = secrets.authenticators("volkswagen.de")
            username, _, password = secret
        except TypeError:
            if not args.username:
                LOG.error('volkswagen.de entry was not found in %s netrc-file. Create it or provide at least a username'
                          ' with --username', netRcFilename)
                sys.exit(1)
            username = args.username
            password = getpass.getpass()
        except FileNotFoundError:
            if not args.username:
                LOG.error('%s netrc-file was not found. Create it or provide at least a username with --username',
                          netRcFilename)
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
        if args.netrc is not None:
            netRcFilename = args.netrc
        else:
            netRcFilename = defaultNetRc
        try:
            secrets = netrc.netrc(file=args.netrc)
            authenticator = secrets.authenticators(args.mqttbroker)
            if authenticator is not None:
                mqttusername, _, mqttpassword = authenticator
        except FileNotFoundError:
            if args.netrc is not None:
                LOG.error('%s netrc-file was not found. Create it or provide at least a username with --username',
                          netRcFilename)
                sys.exit(1)

    mqttCLient = WeConnectMQTTClient(clientId=args.mqttclientid, transport=args.transport, interval=args.interval,
                                     prefix=args.prefix, ignore=args.ignore, updateCapabilities=(not args.noCapabilities),
                                     updatePictures=args.pictures)
    mqttCLient.enable_logger()

    if usetls:
        if args.tls_version == "tlsv1.2":
            tlsVersion = ssl.PROTOCOL_TLSv1_2
        elif args.tls_version == "tlsv1.1":
            tlsVersion = ssl.PROTOCOL_TLSv1_1
        elif args.tls_version == "tlsv1":
            tlsVersion = ssl.PROTOCOL_TLSv1
        elif args.tls_version is None:
            tlsVersion = None
        else:
            LOG.warning('Unknown TLS version %s - ignoring', args.tls_version)
            tlsVersion = None

        if not args.insecure:
            certRequired = ssl.CERT_REQUIRED
        else:
            certRequired = ssl.CERT_NONE

        mqttCLient.tls_set(ca_certs=args.cacerts, certfile=args.cert, keyfile=args.key, cert_reqs=certRequired,
                           tls_version=tlsVersion)
        if args.insecure:
            mqttCLient.tls_insecure_set(True)

    if mqttusername is not None:
        mqttCLient.username_pw_set(username=mqttusername, password=mqttpassword)

    try:
        mqttCLient.connectWeConnect(username=username, password=password, maxAgePictures=args.pictureCache)

        if args.chargingLocation is not None:
            latitude, longitude = args.chargingLocation
            if latitude < -90 or latitude > 90:
                LOG.error('latitude must be between -90 and 90')
                sys.exit(1)
            if longitude < -180 or longitude > 180:
                LOG.error('longitude must be between -180 and 180')
                sys.exit(1)
            mqttCLient.weConnect.latitude = latitude
            mqttCLient.weConnect.longitude = longitude
        mqttCLient.weConnect.searchRadius = args.chargingLocationRadius

        while True:
            try:
                mqttCLient.connect(args.mqttbroker, args.mqttport, args.mqttkeepalive)
                break
            except ConnectionRefusedError as e:
                LOG.error('Could not connect to MQTT-Server: %s, will retry in 10 seconds', e)
                time.sleep(10)

        # blocking run
        mqttCLient.run()
        mqttCLient.disconnect()
        mqttCLient.weConnect.persistTokens()
    except KeyboardInterrupt:
        pass
    except weconnect.AuthentificationError as e:
        errorMessage = f'There was a problem when authenticating with WeConnect: {e}'
        mqttCLient.setError(code=WeConnectErrors.AUTHENTIFICATION, message=errorMessage)
        LOG.critical(errorMessage)
    except weconnect.APICompatibilityError as e:
        errorMessage = f'There was a problem when communicating with WeConnect.  If this problem persists please open a bug report: {e}'
        mqttCLient.setError(code=WeConnectErrors.API_COMPATIBILITY, message=errorMessage)
        LOG.critical(errorMessage)
    finally:
        mqttCLient.disconnect()


class WeConnectMQTTClient(paho.mqtt.client.Client):  # pylint: disable=too-many-instance-attributes
    def __init__(self, clientId=None, transport='tcp', interval=300, prefix='weconnect/0', ignore=0, updateCapabilities=True, updatePictures=True):
        super().__init__(client_id=clientId, transport=transport)
        self.weConnect = None
        self.prefix = prefix
        self.interval = interval
        self.connected = False
        self.hasError = None
        self.ignore = ignore
        self.lastSubscribe = None
        self.updateCapabilities = updateCapabilities
        self.updatePictures = updatePictures

        self.on_connect = self.on_connect_callback
        self.on_message = self.on_message_callback
        self.on_disconnect = self.on_disconnect_callback
        self.on_subscribe = self.on_subscribe_callback

        self.will_set(topic=f'{self.prefix}/mqtt/weconnectConnected', qos=1, retain=True, payload=False)

    def disconnect(self, reasoncode=None, properties=None):
        disconectPublish = self.publish(topic=f'{self.prefix}/mqtt/weconnectConnected', qos=1, retain=True,
                                        payload=False)
        disconectPublish.wait_for_publish()
        super().disconnect(reasoncode, properties)

    def connectWeConnect(self, username, password, maxAgePictures):
        LOG.info('Connect to WeConnect')
        self.weConnect = weconnect.WeConnect(username=username, password=password, updateAfterLogin=False, updateCapabilities=self.updateCapabilities,
                                             updatePictures=self.updatePictures, maxAgePictures=maxAgePictures)
        self.weConnect.addObserver(self.onWeConnectEvent, addressable.AddressableLeaf.ObserverEvent.VALUE_CHANGED
                                   | addressable.AddressableLeaf.ObserverEvent.ENABLED | addressable.AddressableLeaf.ObserverEvent.DISABLED,
                                   priority=addressable.AddressableLeaf.ObserverPriority.USER_MID)
        self.setConnected(connected=True)
        self.setError(code=WeConnectErrors.SUCCESS)

    def updateWeConnect(self):
        LOG.info('Update data from WeConnect')
        try:
            self.weConnect.update(updateCapabilities=self.updateCapabilities, updatePictures=self.updatePictures)
            self.setConnected(connected=True)
            self.setError(code=WeConnectErrors.SUCCESS)
            self.publish(topic=f'{self.prefix}/mqtt/weconnectUpdated', qos=1, retain=True,
                         payload=datetime.utcnow().replace(microsecond=0, tzinfo=timezone.utc).isoformat())
        except errors.RetrievalError:
            self.setConnected(connected=False)
            errorMessage = f'Retrieval error during update. Will try again after configured interval of {self.interval}s'
            self.setError(code=WeConnectErrors.RETRIEVAL_FAILED, message=errorMessage)
            LOG.info(errorMessage)
        except errors.APICompatibilityError:
            self.setConnected(connected=False)
            errorMessage = f'API compatibility error during update. Will try again after configured interval of {self.interval}s'
            self.setError(code=WeConnectErrors.API_COMPATIBILITY, message=errorMessage)
            LOG.info(errorMessage)

    def onWeConnectEvent(self, element, flags):
        if flags & addressable.AddressableLeaf.ObserverEvent.ENABLED:
            if isinstance(element, addressable.ChangeableAttribute):
                LOG.debug('Subscribe for attribute %s%s', self.prefix, element.getGlobalAddress())
                self.subscribe(f'{self.prefix}{element.getGlobalAddress()}', qos=1)
        elif flags & addressable.AddressableLeaf.ObserverEvent.VALUE_CHANGED:
            if isinstance(element.value, (str, int, float)) or element.value is None:
                convertedValue = element.value
            elif isinstance(element.value, Enum):
                convertedValue = element.value.value
            elif isinstance(element.value, Image.Image):
                convertedValue = util.imgToASCIIArt(element.value, columns=120, mode=ascii_magic.Modes.ASCII)
            else:
                convertedValue = str(element.value)
            LOG.debug('%s%s, value changed: new value is: %s', self.prefix, element.getGlobalAddress(), convertedValue)
            self.publish(topic=f'{self.prefix}{element.getGlobalAddress()}', qos=1, retain=True, payload=convertedValue)
        elif flags & addressable.AddressableLeaf.ObserverEvent.DISABLED:
            LOG.debug('%s%s, value is diabled', self.prefix, element.getGlobalAddress())
            self.publish(topic=f'{self.prefix}{element.getGlobalAddress()}', qos=1, retain=True, payload='')

    def setConnected(self, connected=True):
        if connected != self.connected:
            self.publish(topic=f'{self.prefix}/mqtt/weconnectConnected', qos=1, retain=True, payload=connected)
            self.connected = connected

    def setError(self, code=None, message=''):
        if code is None:
            code = WeConnectErrors.SUCCESS
        if code != WeConnectErrors.SUCCESS or message != '' or self.hasError is None or self.hasError:
            self.publish(topic=f'{self.prefix}/mqtt/error/code', qos=1, retain=False, payload=code.value)
            self.publish(topic=f'{self.prefix}/mqtt/error/message', qos=1, retain=False, payload=message)
        if code != WeConnectErrors.SUCCESS:
            self.hasError = True
        else:
            self.hasError = False

    def on_connect_callback(self, mqttc, obj, flags, rc):
        del mqttc  # unused
        del obj  # unused
        del flags  # unused

        if rc == 0:
            LOG.info('Connected to MQTT broker')
            self.publish(topic=f'{self.prefix}/mqtt/weconnectForceUpdate', qos=1, payload=False)
            self.subscribe(f'{self.prefix}/mqtt/weconnectForceUpdate', qos=2)

            self.publish(topic=f'{self.prefix}/mqtt/weconnectUpdateInterval_s', qos=1, retain=True,
                         payload=self.interval)
            self.subscribe(f'{self.prefix}/mqtt/weconnectUpdateInterval_s', qos=1)

            self.setConnected()

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

    def on_disconnect_callback(self, client, userdata, rc):
        del client
        del userdata

        if rc == 0:
            LOG.info('Client successfully disconnected')
        else:
            LOG.info('Client unexpectedly disconnected (%d), trying to reconnect', rc)
            while True:
                try:
                    self.reconnect()
                    break
                except ConnectionRefusedError as e:
                    LOG.error('Could not reconnect to MQTT-Server: %s, will retry in 10 seconds', e)
                except socket.timeout:
                    LOG.error('Could not reconnect to MQTT-Server due to timeout, will retry in 10 seconds')
                finally:
                    time.sleep(10)

    def on_subscribe_callback(self, mqttc, obj, mid, granted_qos):
        del mqttc  # unused
        del obj  # unused
        del mid  # unused
        del granted_qos  # unused
        self.lastSubscribe = datetime.now()
        LOG.debug('sucessfully subscribed to topic')

    def on_message_callback(self, mqttc, obj, msg):  # noqa: C901
        del mqttc  # unused
        del obj  # unused
        if self.ignore > 0 and self.lastSubscribe is not None and (datetime.now() - self.lastSubscribe) < timedelta(seconds=self.ignore):
            LOG.info('ignoring message from broker as it is withing --ignore-for delta')
        elif len(msg.payload) == 0:
            LOG.debug('ignoring empty message')
        elif msg.topic == f'{self.prefix}/mqtt/weconnectForceUpdate':
            if msg.payload.lower() == b'True'.lower():
                LOG.info('Update triggered by MQTT message')
                self.updateWeConnect()
                self.publish(topic=f'{self.prefix}/mqtt/weconnectForceUpdate', qos=2, payload=False)
        elif msg.topic == f'{self.prefix}/mqtt/weconnectUpdateInterval_s':
            if str(msg.payload.decode()).isnumeric():
                newInterval = int(msg.payload)
                if newInterval < 300:
                    errorMessage = f'New intervall of {msg.payload.decode()}s by MQTT message is too low. Minimum is 300s'
                    self.publish(topic=f'{self.prefix}/mqtt/weconnectUpdateInterval_s', qos=1, retain=True,
                                 payload=self.interval)
                elif newInterval > 3500:
                    errorMessage = f'New intervall of {msg.payload.decode()}s by MQTT message is too large. Maximum is 3500s'
                    self.setError(code=WeConnectErrors.INTERVAL_NOT_A_NUMBER, message=errorMessage)
                    LOG.error(errorMessage)
                    self.publish(topic=f'{self.prefix}/mqtt/weconnectUpdateInterval_s', qos=1, retain=True,
                                 payload=self.interval)
                else:
                    self.interval = newInterval
                    LOG.info('New intervall set to %ds by MQTT message', self.interval)
            else:
                errorMessage = f'MQTT message for new interval does not contain a number: {msg.payload.decode()}'
                self.setError(code=WeConnectErrors.INTERVAL_NOT_A_NUMBER, message=errorMessage)
                LOG.error(errorMessage)
                self.publish(topic=f'{self.prefix}/mqtt/weconnectUpdateInterval_s', qos=1, retain=True, payload=self.interval)
        else:
            if msg.topic.startswith(self.prefix):
                address = msg.topic[len(self.prefix):]
                attribute = self.weConnect.getByAddressString(address)
                if isinstance(attribute, addressable.ChangeableAttribute):
                    try:
                        attribute.value = msg.payload.decode()
                        self.setError(code=WeConnectErrors.SUCCESS)
                    except ValueError as valueError:
                        errorMessage = f'Error setting value: {valueError}'
                        self.setError(code=WeConnectErrors.SET_FORMAT, message=errorMessage)
                        LOG.info(errorMessage)
                    except errors.SetterError as setterError:
                        errorMessage = f'Error setting value: {setterError}'
                        self.setError(code=WeConnectErrors.SET_ERROR, message=errorMessage)
                        LOG.info(errorMessage)
                else:
                    errorMessage = f'Trying to change item that is not a changeable attribute {msg.topic}: {msg.payload}'
                    self.setError(code=WeConnectErrors.MESSAGE_NOT_UNDERSTOOD, message=errorMessage)
                    LOG.error(errorMessage)
            else:
                errorMessage = f'I don\'t understand message {msg.topic}: {msg.payload}'
                self.setError(code=WeConnectErrors.ATTRIBUTE_NOT_CHANGEABLE, message=errorMessage)
                LOG.error(errorMessage)

    def run(self):
        self.loop_start()
        try:
            while True:
                time.sleep(self.interval)
                self.updateWeConnect()
        except KeyboardInterrupt:
            self.loop_stop(force=False)


class WeConnectErrors(Enum):
    SUCCESS = 0
    ATTRIBUTE_NOT_CHANGEABLE = -1
    MESSAGE_NOT_UNDERSTOOD = -2
    INTERVAL_NOT_A_NUMBER = -3
    INTERVAL_TOO_SMALL = -4
    INTERVAL_TOO_LARGE = -5
    RETRIEVAL_FAILED = -6
    API_COMPATIBILITY = -7
    AUTHENTIFICATION = -8
    SET_FORMAT = -9
    SET_ERROR = -10
