# rpi-sensehat_mqtt

## Introduction

The files here create a service on the _Raspberry Pi_ that works with the SenseHAT from the [astro-pi](https://astro-pi.org/) project and streams its data over MQTT.

This service works on all the Raspberry Pi flavors, as long as they support the SenseHAT.

## Folder structure

The files are here structured in this way:

* `rpi_sensehat_mqtt.py` python script to read the sensors and publish over MQTT
* `rpi_sensehat_mqtt.logrotate` configuration for [logrotate](https://manpages.debian.org/stretch/logrotate/logrotate.8.en.html) to rotate the log file of this script
* `rpi_sensehat_mqtt.env` file to define the environmental variables used while running the background service
* `rpi_sensehat_mqtt.service` file to run the background service
* `setconfiguration.sh` script to configure the system and properly propagate the files in the right folders

## How-to

The main python script `rpi_sensehat_mqtt.py` does the following operations when it runs:
* Reads sensor data
* Creates the MQTT message
* Publish it on the broker

The script logs its operations in the file `/var/log/rpi_broadcaster/rpi_sensehat_mqtt.log`.

The script requires a configuration through environmental variables defined in the `rpi_sensehat_mqtt.env` file.
The available configuration parameters are:
* `RPI_SENSEHAT_MQTT_LOGLEVEL="<desired loglevel>"` the desired log level to be used in the log, as defined by the [python library](https://docs.python.org/3/library/logging.html#levels)
* `RPI_SENSEHAT_MQTT_CYCLE="<desired time cycle>"` the desired time cycle
* `RPI_SENSEHAT_MQTT_BROKER="protocol://address:port"` endpoint of the broker
* `RPI_SENSEHAT_MQTT_TOPIC_TEMPERATURE="<desired topic>"` topic to stream temperature data
* `RPI_SENSEHAT_MQTT_TOPIC_HUMIDITY="<desired topic>"` topic to stream humidity data
* `RPI_SENSEHAT_MQTT_TOPIC_PRESSURE="<desired topic>"` topic to stream pressure data
* `RPI_SENSEHAT_MQTT_TOPIC_ACCELERATION="<desired topic>"` topic to stream acceleration data
* `RPI_SENSEHAT_MQTT_TOPIC_INERTIAL="<desired topic>"` topic to stream inertial data

## Deploy

In order to deploy the configuration, you need to do the following steps

1. Run the file `zip.bat`
1. Transfer the zip file `rpideploy_*.zip` to the desired target machine
1. On the target machine, extract the zip file content
1. run the following command
	```
	<sudo> bash ./setconfiguration.sh
	```

After this has been successfully executed the new service is already running, and it can be managed using

	<sudo> systemctl <command> rpi_sensehat_mqtt.service
