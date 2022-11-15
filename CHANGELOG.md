# Changelog
All notable changes to this project will be documented in this file.

## [Unreleased]
- No unreleased changes so far

## [0.40.4] - 2022-11-15
### Changed
- Updated API to 0.49.0

## [0.40.3] - 2022-10-13
### Changed
- Updated API to 0.48.3

## [0.40.2] - 2022-10-04
### Added
- Add invalid door lock state

### Changed
- Updated API to 0.48.2

## [0.40.1] - 2022-09-23
### Added
- Tire warning light category

### Fixed
- Bug with honk and flash endpoint

### Changed
- Updated API to 0.48.1

## [0.40.0] - 2022-09-19
### Fixed
- fix parsing of empty strings

### Added
- Preparations for Honk and Flash Endpoint
- doorLockStatus attribute added

### Changed
- Show controls only if capability is available
- Updated API to 0.48.0

## [0.39.2] - 2022-08-24
### Fixed
- Allow climatization without external power when the real setting from the car was not received

### Changed
- Updated API to 0.47.1

## [0.39.1] - 2022-08-15
### Changed/Fixed
- Removed -s as shortcut for S-PIN to reseolve conflict with tls option

## [0.39.0] - 2022-08-11
### Added
- Support for S-PIN by adding --spin 1234 or in .netrc file: "account 1234"
- Support for locking/unlocking (selected cars only)

### Changed
- Updated API to 0.47.0

## [0.38.3] - 2022-08-02
### Added
- Attributes for diesel cars
- New status departureTimersStatus & chargingProfilesStatus
- Support for python 3.10

### Changed
- Updated API to 0.46.0

## [0.38.2] - 2022-07-25
### Fixed
- ReadinessStatus is available again after changes in the backend

### Changed
- Updated API to 0.45.1
- Will force a relogin after 6 hours to prevent disapearing items

## [0.38.1] - 2022-07-14
### Added
- Passive mode

## [0.38.0] - 2022-07-14
### Fixed
- Regular relogin to fix problem with data not showing anymore

### Changed
- Refactoring to use WeConnect-mqtt from inside VWsFriend
- Updated API to 0.45.0

## [0.37.2] - 2022-06-28
### Fixed
- Fixed error with warning light icon

### Changed
- Updated API to 0.44.2

## [0.37.1] - 2022-06-28
### Fixed
- Fixed setting climatisation settings (all but climatisationWithoutExternalPower)

### Changed
- Updated API to 0.44.1

## [0.37.0] - 2022-06-28
### Added
- ChargingState: DISCHARGING
- ChargeMode: HOME_STORAGE_CHARGING, IMMEDIATE_DISCHARGING
- window heating control: only for MEB cars
- wake-up control: not for MEB cars
- DevicePlatform: MBB_OFFLINE
- Role: CDIS_UNKNOWN_USER
- UserRoleStatus: DISABLED_HMI, DISABLED_SPIN, DISABLED_PU_SPIN_RESET, CDIS_UNKNOWN_USER

### Changed
- Updated API to 0.44.0

## [0.36.2] - 2022-06-23
### Added
- Added new values for attribute externalPower: unsupported
- Added new values for attribute chragingStatus: unsupported

### Changed
- Updated API to 0.43.2

## [0.36.1] - 2022-06-23
### Added
- Added new values for attribute externalPower: active
- Added new values for attribute ledColor: green, red

### Changed
- Updated API to 0.43.1

## [0.36.0] - 2022-06-22 (Happy birthday Peer!)
### Added
- Added new attributes: externalPower, brandCode, autoUnlockPlugWhenChargedAC, ledColor (warning, it is not yet clear what values are allowed, so use these with caution)

### Changed
- Updated API to 0.43.0

## [0.35.0] - 2022-06-12
### Changed
- Updated API to 0.41.0

### Added
- selective allCapable added to only fetch data that is provided by the car

### Fixed
- Errors in domains are catched and do not produce warnings anymore

## [0.34.0] - 2022-05-12
### Changed
- Updated API to 0.40.0

## [0.33.0] - 2022-04-12
### Added
- Support for warning lights including png icons

### Changed
- Updated API to 0.39.0

## [0.32.0] - 2022-03-23
### Added
- Added option --with-raw-json-topic that publishes all data as a single json string

## [0.31.1] - 2022-03-22
### Changed
- Improved error messages on login errors
- Updated API to 0.38.1

## [0.31.0] - 2022-03-19
### Added
- Added BatteryPowerLevel 'off' in readiness status.
- Added ClimatizationStatus 'invalid'
- Added occurringOn and startTime in singe timer

### Changed
- Updated API to 0.38.0

## [0.30.2] - 2022-03-04
### Fixed
- Catch error when server is not responding correctly during login

### Changed
- Updated API to 0.37.2

## [0.30.1] - 2022-02-28
### Fixed
- Bug in charging control

### Changed
- Updated API to 0.37.1

## [0.30.0] - 2022-02-25
### Fixed
- Requests tracking behaviour
- Catch error when token could not be fetched

### Changed
- Requests changed from list to dict

### Added
- Possibility to use temperature when startng climatisation
- Added fail_no_external_power to generic request status
- Added chargeType attribute to chargingStatus
- Added chargingSettings attribute to chargingStatus

## [0.29.1] - 2022-02-12
### Fixed
- Fixes bug in charging state API fixing procedure

### Changed
- Updated API to 0.36.4

## [0.29.0] - 2022-02-11
### Fixed
- Login to WeConnect works again after changes on login page
- Fixes json output for values that are zero
- Fixes for chargePower, chargeRate and remaining climatisationTime

### Changed
- Refactors the OAuth procedure
- Updated API to 0.36.3

## [0.28.1] - 2022-01-28
### Fixed
- Login to WeConnect works again after changes on login page

### Changed
- Updated API to 0.35.1

## [0.28.0] - 2022-01-24
### Changed
- All writable items have now two topics: topicname and topicname_writetopic ***Warning this is a breaking change in the topic naming, you have to change your subscriptions!***
  ***Sorry! I was fed up with the way MQTT behaves when you subscribe to the same topic you publish to.***
- Updated API to 0.35.0

### Fixed
- The changes fix several problems when messages are received that were published by WeConnect-MQTT itself

## [0.27.1] - 2022-01-23
### Fixed
- Fixed the conversion error when setting a wrong value

## [0.27.0] - 2022-01-23
### Changed
- All selective topics are now under "domains" topic ***Warning this is a breaking change in the topic naming, you have to change your subscriptions!***
- Control commands are now much faster feedbacking due to a new feature that tracks if the command was successful
- Updated API to 0.34.0

## [0.26.2] - 2022-01-18
### Fixed
- Add new tags attribute

### Changed
- Updated API to 0.33.0

## [0.26.1] - 2022-01-17
### Fixed
- Catch socket error and retry after interval
- Fixed a problem where the temperature of the climatization is always set to 20.5 C

### Changed
- Updated API to 0.32.1

## [0.26.0] - 2022-01-15
### Added
- Add parameter --picture-format to allow publishing pictures through mqtt as png (--picture-format png)

## [0.25.1] - 2022-01-14
### Fixed
- Change datatype for chargePower_kW and chargeRate_kmph from Integer to Float

### Changed
- Updated API to 0.32.0

## [0.25.0] - 2022-01-14
### Added
- Add parameter --republish-on-update to publish on every update from server, not only on value changes

## [0.24.1] - 2022-01-12
### Fixed
- Fix problem with stored tokens
- Hide 504 gateway_timeout error on missing parking position

### Changed
- Updated API to 0.30.4

## [0.24.0] - 2022-01-11
### Added
- new topics /mqtt/topics and /mqtt/writeableTopics that provide all known topics
- new parameter --list-topics to print out new known topics to console

### Fixed
- Missing connection on startup
- More robust against server errors
- Hides status 204 on missing parking position

### Changed
- Updated API to 0.30.3

## [0.23.2] - 2022-01-10
### Fixed
- timezone problem fixed

### Changed
- Updated API to 0.30.2

## [0.23.1] - 2022-01-10
### Fixed
- missing init file in API

### Changed
- Updated API to 0.30.1

## [0.23.0] - 2022-01-10
### Fixed
- no-capabilities fixed

### Added
- selective option that allows to only fetch a subset of the data
- Make result from control commands more responsive

### Changed
- Updated API to 0.30.0

## [0.22.0] - 2022-01-05
### Changed
- ***Warning, the topics changed due to conflicts within the status names from recent changes at WeConnect***
- API is using new url enpoints now
- Updated API to 0.29.0

### Fixed
- Conflicts when simplejson is installed and preferred from requests

### Added
- Added MBB Platform
- New logging configuration parameters

## [0.21.0] - 2021-12-20
### Added
- decoding of capability status
- new charge modes
- new plug states
- new engine and car types
- new status capabilitiesStatus

### Changed
- Only fetch parking position if the capability is enabled
- Updated API to 0.28.0

## [0.20.0] - 2021-12-08
### Added
- Add new gasoline car type

## [0.19.1] - 2021-12-01
### Fixed
- Fixed missing readiness_status module
### Changed
- Updated API to 0.25.1

## [0.19.0] - 2021-12-01
### Added
- Add new status fail_battery_low
- Add new attributes readinessStatus, readinessBatterySupportStatus and devicePlatform

### Changed
- Updated API to 0.25.0

## [0.18.0] - 2021-11-25
### Added
- Add new Charging State CHARGE_PURPOSE_REACHED_CONSERVATION

### Changed
- Updated API to 0.24.0

## [0.17.1] - 2021-11-19
### Fixed
- Corrected addressing of climatization timers

### Changed
- Updated API to 0.23.1

## [0.17.0] - 2021-11-19
### Added
- Add new Charging State CHARGE_PURPOSE_REACHED_NOT_CONSERVATION_CHARGING

### Changed
- Updated API to 0.23.0

## [0.16.3] - 2021-11-04
### Fixed
- Handle timeout during reconnect

### Changed
- Updated API to 0.22.1

## [0.16.2] - 2021-11-01
### Changed
- Updated API to 0.22.0

## [0.16.1] - 2021-10-22
### Fixed
- Fix badge for unlocked vehicle
- Fixes picture caching
- Will delete cache file if cache is corrupted

### Changed
- Updated API to 0.21.5
- Updated paho-mqtt requirement from 1.5.1 to 1.6.1

## [0.16.0] - 2021-10-15
### Changed
- Updated API to 0.21.3
- Changed name of base module

## [0.15.0] - 2021-10-06
### Fixed
- Climate settings and start stop

### Changed
- Updated API to 0.21.0

## [0.14.15] - 2021-09-27
### Fixed
- Fixed resetting of parkingposition while driving

### Added
- New attributes: electricRange, gasolineRange

### Changed
- API updated to 0.20.14

## [0.14.14] - 2021-09-23
### Fixed
- Fixed problems coming from changes in the API

### Added
- New images with badges
- New attributes: odometerMeasurement, rangeMeasurements, unitInCar, targetTemperature_F

### Changed
- API updated to 0.20.12

## [0.14.13] - 2021-09-16
### Fixed
- Fixes previous release that did not take new exceptions into account

## [0.14.12] - 2021-09-15
### Added
- Will retry a request 3 times to try to make instable server connection more stable

### Fixed
- Problem when token could not be refreshed

### Changed
- API updated to 0.20.10

## [0.14.11] - 2021-09-10
### Fixed
- Fix if range is corrupted

## [0.14.10] - 2021-09-02
### Fixed
- Allow forbidden (403) return code for parking position
- Continue fetching data even if retrieval for one car fails

### Changed
- API version to 0.20.6

## [0.14.9] - 2021-09-02
### Fixed
- Fixed UnboundLocalError in condition GDC_MISSING

### Changed
- API version to 0.20.5

## [0.14.8] - 2021-09-01
### Fixed
- Fixed parsing mqttport argument

## [0.14.7] - 2021-09-01
### Fixed
- typing error on python 3.7

### Changed
- API version to 0.20.4

## [0.14.6] - 2021-08-30
### Fixed
- Display of consent url fixed

### Added
- Added new error state delayed

### Changed
- API version to 0.20.3

## [0.14.5] - 2021-08-26
### added
- New error messages for parking position
- New error state: fail_ignition_on

### Changed
- API version to 0.20.2

## [0.14.4] - 2021-08-25
### Added
- New error state: fail_vehicle_is_offline
- New status: climatisationSettingsRequestStatus

### Changed
- API version to 0.19.3

## [0.14.3] - 2021-08-20
### Fixed
- Fixed bad gateway error with parking position when car is driving

### Changed
- API version to 0.19.2

## [0.14.2] - 2021-08-19
### Fixed
- Parking position after weconnect API change

### Changed
- API version to 19.1

## [0.14.1] - 2021-08-15
### Added
- Output of version information after startup

## [0.14.0] - 2021-08-15
### Added
- Possibility to set caching time for picture downloads seperately

### Changed
- Longer caching (24h default) for picture downloads

## [0.13.2] - 2021-08-14
### Fixed
- Bug when downloading pictures fails

### Changed
- Better output of version (adds WeConnect-python version to string)
- Updated API to 0.18.3

## [0.13.1] - 2021-07-30
### Fixed
- Fixes charging and climatization controls

### Changed
- Increase API version to 0.15

## [0.13.0] - 2021-07-28
### Added
- Added invalid WindowHeatingState
- Added invalid ChargeMode
- New statuses lvBatteryStatus (seen for ID vehicles), maintenanceStatus for legacy cars (contains milage and km/days until service) added

## [0.12.2] - 2021-07-26
### Changed
- Improved error message when user consent is missing
- More robust against server side errors when refreshing the tokens
- API updated to version 0.13.2

## [0.12.1] - 2021-07-26
### Fixed
- Import of subpackages

## [0.12.0] - 2021-07-26
### Added
- Dummy for maintenance status (currently no data provided, only error messages)
- Added attribute for chargeMode

### Changed
- More compact string formating
- Changed python API to 0.13.0

## [0.11.4] - 2021-07-25
### Fixed
- Fixed crash due to 404 error when retrieving parking position for cars that don't provide parking positions

## [0.11.3] - 2021-07-18
### Fixed
- Fixed crash due to new elements in the WeConnect API

## [0.11.2] - 2021-07-06
### Changed
- Make docker image smaller
- Release docker image dev versions on edge tag

## [0.11.1] - 2021-07-06
### Fixed
- Build error in Docker file

## [0.11.0] - 2021-07-06
### Added
- Possibility to get data from charging stations with --chargingLocation and --chargingLocationRadius
- Possibility to disable data for capabilities with --no-capabilities
- Possibility to get ASCII ART car and status images (can be disabled with --no-pictures)

## [0.10.1] - 2021-07-03
### Fixed
- Bug with addresses fixed in API 0.11.1

### Changed
- Update API to 0.11.1 to use charging station data

## [0.10.0] - 2021-07-03
### Changed
- Update API to 0.11.0

### Fixed
- More robust against null data in API response

## [0.9.0] - 2021-06-28
### Changed
- Update API to 0.10.0 to use access token instead of id token

## [0.8.2] - 2021-06-21
### Fixed
- Potential problem with finding leaf elements by updating API to 0.8.2
- Missing fail status for target operations by updating API to 0.9.

## [0.8.1] - 2021-06-21
### Fixed
- Wrong error message containing unused attribute

## [0.8.0] - 2021-06-21
### Added
- Support for chargeMode attribute by increasing API version to 0.8.0

## [0.7.0] - 2021-06-21
### Added
- Support for singleTimer attribute (party fixes #7)

## [0.6.2] - 2021-06-18
### Fixed
- Fix for issue #6 when the broker publishes old messages after subscribe

### Changed
- Updating API to Version 0.6.2 fixing several small issues

## [0.6.1] - 2021-06-13
### Changed
- Updating API to Version 0.6.1 to fix bug with obervers

## [0.6.0] - 2021-06-11
### Added
- Support for coUsers attribute

### Changed
- Update API version to 0.6.0

## [0.5.2] - 2021-06-10
### Changed
- Update API version to 0.5.2 to fix bug with charging settings

## [0.5.1] - 2021-06-09
### Changed
- Update API version to 0.5.1

## [0.5.0] - 2021-06-09
### Added
- Possibility to change settings and control the vehicle through MQTT messages

### Changed
- API updated to 0.5.0

## [0.4.0] - 2021-06-06
### Added
Send empty message when topic is disabled
### Changed
- Bump API to 0.4.1

### Fixed
- Crash when server responds with unexpected status code

## [0.3.1] - 2021-06-02
### Changed
- Use API version 0.3.2

## [0.3.0] - 2021-05-31
### Added
- More options for MQTT connection (keepalive, tls, ...)

## [0.2.6] - 2021-05-31
### Fixed
- Correctly use timezone
- Fix problem with caching

## [0.2.0] - 2021-05-28
### Fixed
- Improved error messages for missing netrc files

### Added
- Now comes also with a Docker image
- Default value for .netrc file path shown in help
- Improved error messages for missing netrc files
- Improved error handling for login

## [0.1.0] - 2021-05-27
Initial release

[unreleased]: https://github.com/tillsteinbach/WeConnect-mqtt/compare/v0.40.4...HEAD
[0.40.4]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.40.4
[0.40.3]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.40.3
[0.40.2]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.40.2
[0.40.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.40.1
[0.40.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.40.0
[0.39.2]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.39.2
[0.39.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.39.1
[0.39.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.39.0
[0.38.3]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.38.3
[0.38.2]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.38.2
[0.38.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.38.1
[0.38.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.38.0
[0.37.2]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.37.2
[0.37.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.37.1
[0.37.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.37.0
[0.36.2]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.36.2
[0.36.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.36.1
[0.36.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.36.0
[0.35.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.35.0
[0.34.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.34.0
[0.33.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.33.0
[0.32.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.32.0
[0.31.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.31.1
[0.31.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.31.0
[0.30.2]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.30.2
[0.30.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.30.1
[0.30.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.30.0
[0.29.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.29.1
[0.29.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.29.0
[0.28.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.28.1
[0.28.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.28.0
[0.27.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.27.1
[0.27.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.27.0
[0.26.2]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.26.2
[0.26.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.26.1
[0.26.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.26.0
[0.25.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.25.1
[0.25.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.25.0
[0.24.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.24.1
[0.24.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.24.0
[0.23.2]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.23.2
[0.23.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.23.1
[0.23.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.23.0
[0.22.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.22.0
[0.21.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.21.0
[0.20.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.20.0
[0.19.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.19.1
[0.19.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.19.0
[0.18.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.18.0
[0.17.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.17.1
[0.17.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.17.0
[0.16.3]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.16.3
[0.16.2]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.16.2
[0.16.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.16.1
[0.16.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.16.0
[0.15.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.15.0
[0.14.15]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.14.15
[0.14.14]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.14.14
[0.14.13]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.14.13
[0.14.12]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.14.12
[0.14.11]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.14.11
[0.14.10]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.14.10
[0.14.9]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.14.9
[0.14.8]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.14.8
[0.14.7]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.14.7
[0.14.6]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.14.6
[0.14.5]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.14.5
[0.14.4]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.14.4
[0.14.3]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.14.3
[0.14.2]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.14.2
[0.14.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.14.1
[0.14.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.14.0
[0.13.2]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.13.2
[0.13.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.13.1
[0.13.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.13.0
[0.12.2]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.12.2
[0.12.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.12.1
[0.12.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.12.0
[0.11.4]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.11.4
[0.11.3]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.11.3
[0.11.2]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.11.2
[0.11.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.11.1
[0.11.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.11.0
[0.10.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.10.1
[0.10.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.10.0
[0.9.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.9.0
[0.8.2]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.8.2
[0.8.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.8.1
[0.8.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.8.0
[0.7.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.7.0
[0.6.2]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.6.2
[0.6.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.6.1
[0.6.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.6.0
[0.5.2]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.5.2
[0.5.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.5.1
[0.5.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.5.0
[0.4.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.4.0
[0.3.1]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.3.1
[0.3.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.3.0
[0.2.6]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.2.6
[0.2.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.2.0
[0.1.0]: https://github.com/tillsteinbach/WeConnect-mqtt/releases/tag/v0.1.0
