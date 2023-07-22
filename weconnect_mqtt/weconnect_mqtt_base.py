from datetime import datetime, timedelta, timezone
from enum import Enum
import os
from io import BytesIO
import sys
import socket
import locale
import re
import argparse
import netrc
import getpass
import logging
import time
import ssl

from dateutil import tz

import paho.mqtt.client
from PIL import Image

from requests import exceptions

from weconnect import weconnect, addressable, errors, util, domain
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


def main():  # noqa: C901  # pylint: disable=too-many-branches,too-many-statements,too-many-locals
    parser = argparse.ArgumentParser(
        prog='weconnect-mqtt',
        description='Commandline Interface to interact with the Volkswagen WeConnect Services')
    parser.add_argument('--version', action='version',
                        version=f'%(prog)s {__version__} (using WeConnect-python {__weconnect_version__})')
    brokerGroup = parser.add_argument_group('MQTT and Broker')
    brokerGroup.add_argument('--mqttbroker', type=str, help='Address of MQTT Broker to connect to', required=True)
    brokerGroup.add_argument('--mqttport', type=NumberRangeArgument(1, 65535), help='Port of MQTT Broker. Default is 1883 (8883 for TLS)',
                             required=False, default=None)
    brokerGroup.add_argument('--mqttclientid', required=False, default=None, help='Id of the client. Default is a random id')
    brokerGroup.add_argument('--prefix', help='MQTT topic prefix (default is weconnect/0)', type=str, required=False, default='weconnect/0')
    brokerGroup.add_argument('-k', '--mqttkeepalive', required=False, type=int, default=60, help='Time between keep-alive messages')
    brokerGroup.add_argument('-mu', '--mqtt-username', type=str, dest='mqttusername', help='Username for MQTT broker', required=False)
    brokerGroup.add_argument('-mp', '--mqtt-password', type=str, dest='mqttpassword', help='Password for MQTT broker', required=False)
    brokerGroup.add_argument('-mv', '--mqtt-version', type=str, dest='mqttversion', help='MQTT protocol version used', required=False,
                             choices=['3.1', '3.1.1', '5'], default='3.1.1')
    brokerGroup.add_argument('--transport', required=False, default='tcp', choices=["tcp", 'websockets'], help='EXPERIMENTAL support for websockets transport')
    brokerGroup.add_argument('-s', '--use-tls', action='store_true', help='EXPERIMENTAL')
    brokerGroup.add_argument('--insecure', action='store_true', help='EXPERIMENTAL')
    brokerGroup.add_argument('--cacerts', required=False, default=None, help='EXPERIMENTAL path to the Certificate Authority'
                             ' certificate files that are to be treated as trusted by this client')
    brokerGroup.add_argument('--cert', required=False, default=None, help='EXPERIMENTAL PEM encoded client certificate')
    brokerGroup.add_argument('--key', required=False, default=None, help='EXPERIMENTAL PEM encoded client private key')
    brokerGroup.add_argument('--tls-version', required=False, default=None, choices=['tlsv1.2', 'tlsv1.1', 'tlsv1'],
                             help='EXPERIMENTAL TLS protocol version')
    brokerGroup.add_argument('--ignore-for', dest='ignore', help='Ignore messages for first IGNORE seconds after subscribe to aviod '
                             'retained messages from the broker to make changes to the car (default is 5s) if you don\'t want this behavious set to 0',
                             type=int, required=False, default=5)
    parser.add_argument('--republish-on-update', dest='republishOnUpdate', action='store_true',
                        help='Republish all topics on every update, not just when the value changes.')
    parser.add_argument('--list-topics', dest='listTopics', help='List new topics when created the first time', action='store_true')
    parser.add_argument('--topic-filter-regex', dest='topicFilterRegexString', type=str,
                        default='<PREFIX>/vehicles/[0-9A-Z]+/domains/[a-zA-Z]+/[a-zA-Z]+/request/.*',
                        help='Filter topics by regex. Default is: "<PREFIX>/vehicles/[0-9A-Z]+/domains/[a-zA-Z]+/[a-zA-Z]+/request/.*"')

    weConnectGroup = parser.add_argument_group('WeConnect')
    weConnectGroup.add_argument('-u', '--username', type=str, help='Username of Volkswagen id', required=False)
    weConnectGroup.add_argument('-p', '--password', type=str, help='Password of Volkswagen id', required=False)
    weConnectGroup.add_argument('--spin', help='S-PIN of Volkswagen id, required for selected commands', required=False, nargs='?', action='store',
                                default=None, const=True)
    defaultNetRc = os.path.join(os.path.expanduser("~"), ".netrc")
    weConnectGroup.add_argument('--netrc', help=f'File in netrc syntax providing login (default: {defaultNetRc}).'
                                ' Netrc is only used when username and password are not provided  as arguments', default=None, required=False)
    weConnectGroup.add_argument('-i', '--interval', help='Query interval in seconds',
                                type=NumberRangeArgument(300, 3500), required=False, default=300)
    weConnectGroup.add_argument('--picture-cache-interval', dest='pictureCache', help='Picture download interval in seconds, this does not influence the'
                                ' interval in which the status picture is updated', type=NumberRangeArgument(1), required=False, default=86400)

    weConnectGroup.add_argument('-l', '--chargingLocation', nargs=2, metavar=('latitude', 'longitude'), type=float,
                                help='If set charging locations will be added to the result around the given coordinates')
    weConnectGroup.add_argument('--chargingLocationRadius', type=NumberRangeArgument(0, 100000),
                                help='Radius in meters around the chargingLocation to search for chargers')
    weConnectGroup.add_argument('--no-capabilities', dest='noCapabilities', help='Do not add capabilities', action='store_true')
    weConnectGroup.add_argument('--selective', help='Just fetch status of a certain type', default=None, required=False, action='append',
                                type=domain.Domain, choices=list(domain.Domain))
    weConnectGroup.add_argument('--convert-times', dest='convertTimes',
                                help='Convert all times from UTC to timezone, e.g. --convert-times \'Europe/Berlin\', leave empty to use system timezone',
                                nargs='?', const='', default=None, type=str)
    weConnectGroup.add_argument('--timeformat', dest='timeFormat',
                                help='Convert times using the timeformat provided default is ISO format, leave argument empty to use system default',
                                nargs='?', const='', default=None, type=str)
    weConnectGroup.add_argument('--locale',
                                help='Use specified locale, leave argument empty to use system default', default='', type=str)
    parser.add_argument('--pictures', help='Add ASCII art pictures', action='store_true')
    parser.add_argument('--picture-format', dest='pictureFormat', help='Format of the picture topics', default=PictureFormat.TXT, required=False,
                        type=PictureFormat, choices=list(PictureFormat))
    parser.add_argument('--with-raw-json-topic', dest='withRawJsonTopic', help='Adds topic <PREFIX>/rawjson with all information in one json string.'
                        ' Topic is updated on change only', action='store_true')

    loggingGroup = parser.add_argument_group('Logging')
    loggingGroup.add_argument('-v', '--verbose', action="append_const", help='Logging level (verbosity)', const=-1,)
    loggingGroup.add_argument('--logging-format', dest='loggingFormat', help='Logging format configured for python logging '
                              '(default: %%(asctime)s:%%(levelname)s:%%(module)s:%%(message)s)', default='%(asctime)s:%(levelname)s:%(module)s:%(message)s')
    loggingGroup.add_argument('--logging-date-format', dest='loggingDateFormat', help='Logging format configured for python logging '
                              '(default: %%Y-%%m-%%dT%%H:%%M:%%S%%z)', default='%Y-%m-%dT%H:%M:%S%z')
    loggingGroup.add_argument('--hide-repeated-log', dest='hideRepeatedLog', help='Hide repeated log messages from the same module', action='store_true')

    args = parser.parse_args()
    try:
        locale.setlocale(locale.LC_ALL, args.locale)
        if args.timeFormat == '':
            args.timeFormat = locale.nl_langinfo(locale.D_T_FMT)
    except locale.Error as err:
        LOG.error('Cannot set locale: %s', err)
        sys.exit(1)

    logLevel = LOG_LEVELS.index(DEFAULT_LOG_LEVEL)
    for adjustment in args.verbose or ():
        logLevel = min(len(LOG_LEVELS) - 1, max(logLevel + adjustment, 0))

    logging.basicConfig(level=LOG_LEVELS[logLevel], format=args.loggingFormat, datefmt=args.loggingDateFormat)
    if args.hideRepeatedLog:
        for handler in logging.root.handlers:
            handler.addFilter(util.DuplicateFilter())
    LOG.info('WeConnect-mqtt %s (using WeConnect-python %s)', __version__, __weconnect_version__)

    if args.mqttversion == '3.1':
        mqttVersion = paho.mqtt.client.MQTTv31
    elif args.mqttversion == '5':
        mqttVersion = paho.mqtt.client.MQTTv5
    else:
        mqttVersion = paho.mqtt.client.MQTTv311

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
    spin = None

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
        except netrc.NetrcParseError as err:
            LOG.error('Authentification using .netrc failed: %s', err)
            sys.exit(1)
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

    if args.spin is not None:
        spin = args.spin
    else:
        if args.netrc is not None:
            netRcFilename = args.netrc
        else:
            netRcFilename = defaultNetRc
        try:
            secrets = netrc.netrc(file=args.netrc)
            _, account, _ = secrets.authenticators("volkswagen.de")
            if account is not None:
                spin = account
        except netrc.NetrcParseError as err:
            LOG.error('Authentification using .netrc failed: %s', err)
            sys.exit(1)
        except TypeError:
            pass
        except FileNotFoundError:
            pass
    if spin is not None and not isinstance(spin, bool):
        if len(spin) == 0:
            spin = None
        elif not re.match(r"^\d{4}$", spin):
            LOG.error('S-PIN: %s needs to be a four digit number', spin)
            sys.exit(1)

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

    try:
        topicFilterRegexString = args.topicFilterRegexString
        topicFilterRegexString.replace('<PREFIX>', args.prefix)
        topicFilterRegex = re.compile(args.topicFilterRegexString)
    except re.error as err:
        LOG.error('Problem with provided regex %s: %s', topicFilterRegexString, err)
        sys.exit(1)

    convertTimezone = None
    if args.convertTimes is not None:
        if args.convertTimes == '':
            convertTimezone = datetime.now().astimezone().tzinfo
        else:
            convertTimezone = tz.gettz(args.convertTimes)

    mqttCLient = WeConnectMQTTClient(clientId=args.mqttclientid, protocol=mqttVersion, transport=args.transport, interval=args.interval,
                                     prefix=args.prefix, ignore=args.ignore, updateCapabilities=(not args.noCapabilities),
                                     updatePictures=args.pictures, selective=args.selective, listNewTopics=args.listTopics,
                                     republishOnUpdate=args.republishOnUpdate, pictureFormat=args.pictureFormat, topicFilterRegex=topicFilterRegex,
                                     convertTimezone=convertTimezone, timeFormat=args.timeFormat, withRawJsonTopic=args.withRawJsonTopic)
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
        while True:
            try:
                weConnect = weconnect.WeConnect(username=username, password=password, spin=spin, updateAfterLogin=False,
                                                updateCapabilities=mqttCLient.updateCapabilities, updatePictures=mqttCLient.updatePictures,
                                                maxAgePictures=args.pictureCache, selective=mqttCLient.selective,
                                                forceReloginAfter=21600, timeout=180)
                mqttCLient.connectWeConnect(weConnect)
                break
            except exceptions.ConnectionError as e:
                LOG.error('Could not connect to VW-Server: %s, will retry in 10 seconds', e)
                time.sleep(10)

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
    except errors.AuthentificationError as e:
        errorMessage = f'There was a problem when authenticating with WeConnect: {e}'
        mqttCLient.setError(code=WeConnectErrors.AUTHENTIFICATION, message=errorMessage)
        LOG.critical(errorMessage)
    except errors.APICompatibilityError as e:
        errorMessage = f'There was a problem when communicating with WeConnect.  If this problem persists please open a bug report: {e}'
        mqttCLient.setError(code=WeConnectErrors.API_COMPATIBILITY, message=errorMessage)
        LOG.critical(errorMessage)
    finally:
        mqttCLient.disconnect()


class WeConnectMQTTClient(paho.mqtt.client.Client):  # pylint: disable=too-many-instance-attributes
    def __init__(self, clientId=None, protocol=paho.mqtt.client.MQTTv311, transport='tcp', interval=300,  # pylint: disable=too-many-arguments
                 prefix='weconnect/0', ignore=0, updateCapabilities=True, updatePictures=True, selective=None, listNewTopics=False, republishOnUpdate=False,
                 pictureFormat=None, topicFilterRegex=None, convertTimezone=None, timeFormat=None, withRawJsonTopic=False, passive=False,
                 updateOnConnect=True):
        super().__init__(client_id=clientId, transport=transport, protocol=protocol)
        self.weConnect = None
        self.prefix = prefix
        self.interval = interval
        self.connected = False
        self.hasError = None
        self.ignore = ignore
        self.lastSubscribe = None
        self.updateCapabilities = updateCapabilities
        self.updatePictures = updatePictures
        self.pictureFormat = pictureFormat
        self.selective = selective
        self.listNewTopics = listNewTopics
        self.topics = []
        self.topicsChanged = False
        self.writeableTopics = []
        self.writeableTopicsChanged = False
        self.republishOnUpdate = republishOnUpdate
        self.topicFilterRegex = topicFilterRegex
        self.convertTimezone = convertTimezone
        self.timeFormat = timeFormat
        self.hasChanges = False
        self.withRawJsonTopic = withRawJsonTopic
        self.passive = passive
        self.updateOnConnect = updateOnConnect

        if protocol == paho.mqtt.client.MQTTv5:
            self.on_connect = self.on_connect_callback_v5
            self.on_message = self.on_message_callback
            self.on_disconnect = self.on_disconnect_callback_v5
            self.on_subscribe = self.on_subscribe_callback_v5
        else:
            self.on_connect = self.on_connect_callback
            self.on_message = self.on_message_callback
            self.on_disconnect = self.on_disconnect_callback
            self.on_subscribe = self.on_subscribe_callback

        self.will_set(topic=f'{self.prefix}/mqtt/weconnectConnected', qos=1, retain=True, payload=False)

    def addTopic(self, topic, writeable=False):
        if topic not in self.topics:
            if writeable:
                self.writeableTopics.append(topic)
                self.writeableTopics.sort()
                self.writeableTopicsChanged = True
            else:
                self.topics.append(topic)
                self.topics.sort()
                self.topicsChanged = True

            if self.listNewTopics:
                print(f'New topic: {topic}{" (writeable)" if writeable else ""}', flush=True)

    def publishTopics(self):
        if self.topicsChanged:
            self.topicsChanged = False
            topicstopic = f'{self.prefix}/mqtt/topics'
            content = ',\n'.join(self.topics)
            self.publish(topic=topicstopic, qos=1, retain=True, payload=content)
            if topicstopic not in self.topics:
                self.addTopic(topicstopic)

        if self.writeableTopicsChanged:
            self.writeableTopicsChanged = False
            writeabletopicstopic = f'{self.prefix}/mqtt/writeableTopics'
            content = ',\n'.join(self.writeableTopics)
            self.publish(topic=writeabletopicstopic, qos=1, retain=True, payload=content)
            if writeabletopicstopic not in self.topics:
                self.addTopic(writeabletopicstopic)

    def disconnect(self, reasoncode=None, properties=None):
        try:
            disconectPublish = self.publish(topic=f'{self.prefix}/mqtt/weconnectConnected', qos=1, retain=True,
                                            payload=False)
            disconectPublish.wait_for_publish()
        except RuntimeError:
            pass
        super().disconnect(reasoncode, properties)

    def connectWeConnect(self, weConnect):
        LOG.info('Connect to WeConnect')
        self.weConnect = weConnect
        self.weConnect.enableTracker()
        if self.republishOnUpdate:
            flags = (addressable.AddressableLeaf.ObserverEvent.UPDATED_FROM_SERVER  # pylint: disable=unsupported-binary-operation
                     | addressable.AddressableLeaf.ObserverEvent.ENABLED  # pylint: disable=unsupported-binary-operation
                     | addressable.AddressableLeaf.ObserverEvent.DISABLED)  # pylint: disable=unsupported-binary-operation
        else:
            flags = (addressable.AddressableLeaf.ObserverEvent.VALUE_CHANGED  # pylint: disable=unsupported-binary-operation
                     | addressable.AddressableLeaf.ObserverEvent.ENABLED  # pylint: disable=unsupported-binary-operation
                     | addressable.AddressableLeaf.ObserverEvent.DISABLED)  # pylint: disable=unsupported-binary-operation
        self.weConnect.addObserver(self.onWeConnectEvent, flags, priority=addressable.AddressableLeaf.ObserverPriority.USER_MID)
        self.setConnected(connected=True)
        self.setError(code=WeConnectErrors.SUCCESS)

    def updateWeConnect(self, reraise=False):  # noqa: C901
        if self.passive:
            return
        LOG.info('Update data from WeConnect')
        self.hasChanges = False
        try:
            self.weConnect.update(updateCapabilities=self.updateCapabilities, updatePictures=self.updatePictures, selective=self.selective, force=True)
            self.setConnected(connected=True)
            self.setError(code=WeConnectErrors.SUCCESS)
            topic = f'{self.prefix}/mqtt/weconnectUpdated'
            convertedTime = datetime.utcnow().replace(microsecond=0, tzinfo=timezone.utc)
            if self.convertTimezone is not None:
                convertedTime = convertedTime.astimezone(self.convertTimezone)
            if self.timeFormat is not None:
                convertedTimeString = convertedTime.strftime(self.timeFormat)
            else:
                convertedTimeString = convertedTime.isoformat()
            self.publish(topic=topic, qos=1, retain=True,
                         payload=convertedTimeString)
            if topic not in self.topics:
                self.addTopic(topic)
        except errors.RetrievalError as error:
            self.setConnected(connected=False)
            errorMessage = f'Retrieval error during update. Will try again after configured interval of {self.interval}s'
            self.setError(code=WeConnectErrors.RETRIEVAL_FAILED, message=errorMessage)
            LOG.info(errorMessage)
            if reraise:
                raise error
        except errors.APICompatibilityError as error:
            self.setConnected(connected=False)
            errorMessage = f'API compatibility error ({str(error)}) during update. Will try again after configured interval of {self.interval}s'
            self.setError(code=WeConnectErrors.API_COMPATIBILITY, message=errorMessage)
            LOG.info(errorMessage)
            if reraise:
                raise error
        except errors.TemporaryAuthentificationError as error:
            self.setConnected(connected=False)
            errorMessage = f'Temporary authentification error during update. Will try again after configured interval of {self.interval}s'
            self.setError(code=WeConnectErrors.AUTHENTIFICATION, message=errorMessage)
            LOG.info(errorMessage)
            if reraise:
                raise error
        except socket.error as error:
            self.setConnected(connected=False)
            errorMessage = f'Socket error during update. Will try again after configured interval of {self.interval}s'
            self.setError(code=WeConnectErrors.RETRIEVAL_FAILED, message=errorMessage)
            LOG.info(errorMessage)
            if reraise:
                raise error
        if self.withRawJsonTopic and self.hasChanges:
            topic = f'{self.prefix}/rawjson'
            if topic not in self.topics:
                self.addTopic(topic)
            json = self.weConnect.toJSON()
            self.publish(topic=topic, qos=1, retain=True, payload=json)
        self.publishTopics()

    def onWeConnectEvent(self, element, flags):  # noqa: C901
        self.hasChanges = True
        topic = f'{self.prefix}{element.getGlobalAddress()}'
        if self.topicFilterRegex is not None and self.topicFilterRegex.match(topic):
            return

        if flags & addressable.AddressableLeaf.ObserverEvent.ENABLED:
            if isinstance(element, addressable.ChangeableAttribute):
                topic = topic + '_writetopic'
                LOG.debug('Subscribe for attribute %s%s', self.prefix, element.getGlobalAddress())
                self.subscribe(topic, qos=1)
                if topic not in self.topics:
                    self.addTopic(topic, writeable=True)
            elif isinstance(element, addressable.AddressableAttribute):
                if topic not in self.topics:
                    self.addTopic(topic)
        elif (flags & addressable.AddressableLeaf.ObserverEvent.VALUE_CHANGED) \
                or (self.republishOnUpdate and (flags & addressable.AddressableLeaf.ObserverEvent.UPDATED_FROM_SERVER)):
            convertedValue = self.convertValue(element.value)
            LOG.debug('%s%s, value changed: new value is: %s', self.prefix, element.getGlobalAddress(), convertedValue)
            self.publish(topic=f'{self.prefix}{element.getGlobalAddress()}', qos=1, retain=True, payload=convertedValue)
        elif flags & addressable.AddressableLeaf.ObserverEvent.DISABLED:
            LOG.debug('%s%s, value is diabled', self.prefix, element.getGlobalAddress())
            self.publish(topic=f'{self.prefix}{element.getGlobalAddress()}', qos=1, retain=True, payload='')

    def convertValue(self, value):
        if isinstance(value, (str, int, float)) or value is None:
            return value
        if isinstance(value, (list)):
            return ', '.join([str(item.value) if isinstance(item, Enum) else str(item) for item in value])
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, datetime):
            convertedTime = value
            if self.convertTimezone is not None:
                convertedTime = value.astimezone(self.convertTimezone)
            if self.timeFormat is not None:
                return convertedTime.strftime(self.timeFormat)
            return str(convertedTime)
        if isinstance(value, Image.Image):
            if self.pictureFormat == PictureFormat.TXT or self.pictureFormat is None:
                return util.imgToASCIIArt(value, columns=120, mode=util.ASCIIModes.ASCII)
            if self.pictureFormat == PictureFormat.PNG:
                img_io = BytesIO()
                value.save(img_io, 'PNG')
                return img_io.getvalue()
            return util.imgToASCIIArt(value, columns=120, mode=util.ASCIIModes.ASCII)
        return str(value)

    def setConnected(self, connected=True):
        if connected != self.connected:
            topic = f'{self.prefix}/mqtt/weconnectConnected'
            self.publish(topic=topic, qos=1, retain=True, payload=connected)
            self.connected = connected
            if topic not in self.topics:
                self.addTopic(topic)

    def setError(self, code=None, message=''):
        if code is None:
            code = WeConnectErrors.SUCCESS
        if code != WeConnectErrors.SUCCESS or message != '' or self.hasError is None or self.hasError:
            topic = f'{self.prefix}/mqtt/error/code'
            self.publish(topic=topic, qos=1, retain=False, payload=code.value)
            if topic not in self.topics:
                self.addTopic(topic)
            topic = f'{self.prefix}/mqtt/error/message'
            self.publish(topic=topic, qos=1, retain=False, payload=message)
            if topic not in self.topics:
                self.addTopic(topic)
        if code != WeConnectErrors.SUCCESS:
            self.hasError = True
        else:
            self.hasError = False

    def on_connect_callback(self, mqttc, obj, flags, rc):  # noqa: C901
        del mqttc  # unused
        del obj  # unused
        del flags  # unused

        if rc == 0:
            LOG.info('Connected to MQTT broker')
            if not self.passive:
                topic = f'{self.prefix}/mqtt/weconnectForceUpdate_writetopic'
                self.subscribe(topic, qos=2)
                if topic not in self.topics:
                    self.addTopic(topic, writeable=True)

                topic = f'{self.prefix}/mqtt/weconnectUpdateInterval_s'
                self.publish(topic=topic, qos=1, retain=True,
                             payload=self.interval)
                self.subscribe(topic + '_writetopic', qos=1)
                if topic not in self.topics:
                    self.addTopic(topic + '_writetopic', writeable=True)

            # Subscribe again to all writeable topics after a reconnect
            for writeableTopic in self.writeableTopics:
                self.subscribe(writeableTopic, qos=1)

            self.setConnected()

            if self.updateOnConnect:
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

    def on_connect_callback_v5(self, mqttc, obj, flags, reasonCode, properties):  # noqa: C901  # pylint: disable=too-many-branches
        del mqttc  # unused
        del obj  # unused
        del flags  # unused
        del properties

        if reasonCode == 0:
            LOG.info('Connected to MQTT broker')
            if not self.passive:
                topic = f'{self.prefix}/mqtt/weconnectForceUpdate_writetopic'
                self.subscribe(topic, qos=2)
                if topic not in self.topics:
                    self.addTopic(topic, writeable=True)

                topic = f'{self.prefix}/mqtt/weconnectUpdateInterval_s'
                self.publish(topic=topic, qos=1, retain=True,
                             payload=self.interval)
                self.subscribe(topic + '_writetopic', qos=1)
                if topic not in self.topics:
                    self.addTopic(topic + '_writetopic', writeable=True)

            # Subscribe again to all writeable topics after a reconnect
            for writeableTopic in self.writeableTopics:
                self.subscribe(writeableTopic, qos=1)

            self.setConnected()

            if self.updateOnConnect:
                self.updateWeConnect()
        elif reasonCode == 128:
            LOG.error('Could not connect (%d): Unspecified error', reasonCode)
        elif reasonCode == 129:
            LOG.error('Could not connect (%d): Malformed packet', reasonCode)
        elif reasonCode == 130:
            LOG.error('Could not connect (%d): Protocol error', reasonCode)
        elif reasonCode == 131:
            LOG.error('Could not connect (%d): Implementation specific error', reasonCode)
        elif reasonCode == 132:
            LOG.error('Could not connect (%d): Unsupported protocol version', reasonCode)
        elif reasonCode == 133:
            LOG.error('Could not connect (%d): Client identifier not valid', reasonCode)
        elif reasonCode == 134:
            LOG.error('Could not connect (%d): Bad user name or password', reasonCode)
        elif reasonCode == 135:
            LOG.error('Could not connect (%d): Not authorized', reasonCode)
        elif reasonCode == 136:
            LOG.error('Could not connect (%d): Server unavailable', reasonCode)
        elif reasonCode == 137:
            LOG.error('Could not connect (%d): Server busy. Retrying in 10 seconds', reasonCode)
            time.sleep(10)
            self.reconnect()
        elif reasonCode == 138:
            LOG.error('Could not connect (%d): Banned', reasonCode)
        elif reasonCode == 140:
            LOG.error('Could not connect (%d): Bad authentication method', reasonCode)
        elif reasonCode == 144:
            LOG.error('Could not connect (%d): Topic name invalid', reasonCode)
        elif reasonCode == 149:
            LOG.error('Could not connect (%d): Packet too large', reasonCode)
        elif reasonCode == 151:
            LOG.error('Could not connect (%d): Quota exceeded', reasonCode)
        elif reasonCode == 154:
            LOG.error('Could not connect (%d): Retain not supported', reasonCode)
        elif reasonCode == 155:
            LOG.error('Could not connect (%d): QoS not supported', reasonCode)
        elif reasonCode == 156:
            LOG.error('Could not connect (%d): Use another server', reasonCode)
        elif reasonCode == 157:
            LOG.error('Could not connect (%d): Server move', reasonCode)
        elif reasonCode == 159:
            LOG.error('Could not connect (%d): Connection rate exceeded', reasonCode)
        else:
            print('Could not connect: %d', reasonCode, file=sys.stderr)
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
                except OSError as e:
                    LOG.error('Could not reconnect to MQTT-Server: %s, will retry in 10 seconds', e)
                finally:
                    time.sleep(10)

    def on_disconnect_callback_v5(self, client, userdata, reasonCode, properties):  # noqa: C901  # pylint: disable=too-many-branches
        del client
        del properties

        if reasonCode == 0:
            LOG.info('Client successfully disconnected')
        elif reasonCode == 4:
            LOG.info('Client successfully disconnected: %s', userdata)
        elif reasonCode == 137:
            LOG.error('Client disconnected: Server busy')
            while True:
                try:
                    self.reconnect()
                    break
                except ConnectionRefusedError as e:
                    LOG.error('Could not reconnect to MQTT-Server: %s, will retry in 10 seconds', e)
                except socket.timeout:
                    LOG.error('Could not reconnect to MQTT-Server due to timeout, will retry in 10 seconds')
                except OSError as e:
                    LOG.error('Could not reconnect to MQTT-Server: %s, will retry in 10 seconds', e)
                finally:
                    time.sleep(10)
        elif reasonCode == 139:
            LOG.error('Client disconnected: Server shutting down')
            while True:
                try:
                    self.reconnect()
                    break
                except ConnectionRefusedError as e:
                    LOG.error('Could not reconnect to MQTT-Server: %s, will retry in 10 seconds', e)
                except socket.timeout:
                    LOG.error('Could not reconnect to MQTT-Server due to timeout, will retry in 10 seconds')
                except OSError as e:
                    LOG.error('Could not reconnect to MQTT-Server: %s, will retry in 10 seconds', e)
                finally:
                    time.sleep(10)
        elif reasonCode == 160:
            LOG.error('Client disconnected: Maximum connect time')
        else:
            LOG.error('Client unexpectedly disconnected (%d), trying to reconnect', reasonCode)
            while True:
                try:
                    self.reconnect()
                    break
                except ConnectionRefusedError as e:
                    LOG.error('Could not reconnect to MQTT-Server: %s, will retry in 10 seconds', e)
                except socket.timeout:
                    LOG.error('Could not reconnect to MQTT-Server due to timeout, will retry in 10 seconds')
                except OSError as e:
                    LOG.error('Could not reconnect to MQTT-Server: %s, will retry in 10 seconds', e)
                finally:
                    time.sleep(10)

    def on_subscribe_callback(self, mqttc, obj, mid, granted_qos):
        del mqttc  # unused
        del obj  # unused
        del mid  # unused
        del granted_qos  # unused
        self.lastSubscribe = datetime.now()
        LOG.debug('sucessfully subscribed to topic')

    def on_subscribe_callback_v5(self, mqttc, obj, mid, reasonCodes, properties):
        del mqttc  # unused
        del obj  # unused
        del mid  # unused
        del properties  # unused
        if any(x in [0, 1, 2] for x in reasonCodes):
            self.lastSubscribe = datetime.now()
            LOG.debug('sucessfully subscribed to topic')
        else:
            LOG.error('Subscribe was not successfull (%s)', ', '.join(reasonCodes))

    def on_message_callback(self, mqttc, obj, msg):  # noqa: C901
        del mqttc  # unused
        del obj  # unused
        if self.ignore > 0 and self.lastSubscribe is not None and (datetime.now() - self.lastSubscribe) < timedelta(seconds=self.ignore):
            LOG.info('ignoring message from broker as it is within --ignore-for delta')
        elif len(msg.payload) == 0:
            LOG.debug('ignoring empty message')
        elif msg.topic == f'{self.prefix}/mqtt/weconnectForceUpdate_writetopic' and not self.passive:
            if msg.payload.lower() == b'True'.lower():
                LOG.info('Update triggered by MQTT message')
                self.updateWeConnect()
                self.publish(topic=f'{self.prefix}/mqtt/weconnectForceUpdate', qos=2, payload=False)
        elif msg.topic == f'{self.prefix}/mqtt/weconnectUpdateInterval_s_writetopic' and not self.passive:
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
                    self.publish(topic=f'{self.prefix}/mqtt/weconnectUpdateInterval_s', qos=1, retain=True,
                                 payload=self.interval)
                    LOG.info('New intervall set to %ds by MQTT message', self.interval)
            else:
                errorMessage = f'MQTT message for new interval does not contain a number: {msg.payload.decode()}'
                self.setError(code=WeConnectErrors.INTERVAL_NOT_A_NUMBER, message=errorMessage)
                LOG.error(errorMessage)
                self.publish(topic=f'{self.prefix}/mqtt/weconnectUpdateInterval_s', qos=1, retain=True, payload=self.interval)
        else:
            if msg.topic.startswith(self.prefix):
                address = msg.topic[len(self.prefix):]
                if address.endswith('_writetopic'):
                    address = address[:-len('_writetopic')]

                    attribute = self.weConnect.getByAddressString(address)
                    if isinstance(attribute, addressable.ChangeableAttribute):
                        try:
                            attribute.value = msg.payload.decode()
                            self.setError(code=WeConnectErrors.SUCCESS)
                            LOG.debug('Successfully set value')
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
                    attribute = self.weConnect.getByAddressString(address)
                    if isinstance(attribute, addressable.ChangeableAttribute):
                        errorMessage = f'Trying to change item on not writeable topic {msg.topic}: {msg.payload}, please use {msg.topic}_writetopic instead'
                        self.setError(code=WeConnectErrors.MESSAGE_NOT_UNDERSTOOD, message=errorMessage)
                        LOG.error(errorMessage)
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
            self.weConnect.disconnect()


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


class PictureFormat(Enum):
    TXT = 'txt'
    PNG = 'png'

    def __str__(self):
        return self.value
