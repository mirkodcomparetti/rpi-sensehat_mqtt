#!/usr/bin/python3
# -*- coding: utf-8 -*-
# This scripts reads sensors from SenseHAT and streams them on MQTT

from sense_hat import SenseHat
import logging
import os
import paho.mqtt.client as mqtt
import uuid
import json
from rfc3986 import urlparse
import signal
from threading import Event
import socket
import time


class RpiSenseHatMqtt:
    """Main app."""

    def __init__(self):
        """Init RpiSenseHatMqtt class."""
        self.logger = logging.getLogger('rpi_sensehat_mqtt.RpiSenseHatMqtt')
        self.initialized = False
        topic_prefix = os.environ.get('RPI_SENSEHAT_MQTT_TOPIC_PREFIX', "sensehat")
        self.topic_prefix = topic_prefix if topic_prefix.endswith("/") else (topic_prefix + "/")
        self.logger.info("Begin initialize class RpiSenseHatMqtt")
        self.logger.debug("Capturing signals")
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)
        self.broker_url = None
        self.broker_port = None
        self.broker_user = None
        if not self._validate_info(
                os.environ.get('RPI_SENSEHAT_MQTT_BROKER', "mqtt://test.mosquitto.org:1883")
        ):
            self.logger.error("Broker information not valid")
        else:
            self.logger.info("Initialize MQTT")
            self.mqtt_client = mqtt.Client(client_id=str(uuid.uuid4()))
            self.mqtt_client.on_connect = self._on_connect
            self.mqtt_client.on_message = self._on_message
            self.mqtt_client.on_publish = self._on_publish
            self.hostname = socket.gethostname()
            self.location = os.environ.get('RPI_SENSEHAT_MQTT_LOCATION', "studio")
            self.measurement = os.environ.get('RPI_SENSEHAT_MQTT_MEASUREMENT', "environment")

            self.logger.info("Initialize SenseHAT")
            self.sense = SenseHat()
            self.sense.clear()
            self.streaming_cycle = int(os.environ.get('RPI_SENSEHAT_MQTT_CYCLE', 60))
            self.streaming_exit = Event()

            self.initialized = True
            self.sense.show_message(os.environ.get('RPI_SENSEHAT_MQTT_WELCOME', "Loaded!"))
            self.sense.low_light = True
            self.logger.info("Done initialize class RpiSenseHatMqtt")

    def cleanup(self, signum, frame):
        self.logger.info("Cleanup")
        self.streaming_exit.set()
        if not self.initialized:
            return None
        if self.mqtt_client.is_connected():
            self.mqtt_client.disconnect()
            self.mqtt_client.loop_stop()

    def _validate_info(self, broker_info):
        self.logger.debug("Validating " + broker_info)
        parseduri = urlparse(broker_info)
        if not (parseduri.scheme in ["mqtt", "ws"]):
            return False
        self.broker_url = parseduri.host
        self.broker_port = parseduri.port
        self.broker_user = parseduri.userinfo
        self.logger.debug("broker_user {}".format(self.broker_user))
        self.logger.debug("broker_url {}, broker_port: {}".format(self.broker_url, self.broker_port))
        if not (self.broker_url and self.broker_port):
            return False
        return True

    def _on_connect(self, client, userdata, flags, rc):
        self.logger.info("Connected with result code " + str(rc))
        self.mqtt_client.subscribe(self.topic_prefix + "commands")

    def _on_message(self, client, userdata, msg):
        self.logger.debug(msg.topic + " " + str(msg.payload))
        if msg.topic in [self.topic_prefix + "commands"]:
            command = json.loads(msg.payload)
            if 'ledwall' in command.keys():
                self.logger.debug("Writing message on the LedWall: {}".format(command["ledwall"]))
                self.sense.show_message(command["ledwall"])

    def _on_publish(self, client, userdata, result):
        pass

    def connect(self):
        if self.initialized and self.broker_url and self.broker_port:
            self.logger.debug("{}:{}".format(self.broker_url, self.broker_port))
            self.mqtt_client.connect(self.broker_url, self.broker_port, 30)

    def _stream_sensors(self):
        while not self.streaming_exit.is_set():
            js_on_message = self._read_sensors()
            js_on_message["measurement"] = self.measurement
            js_on_message["source"] = self.hostname
            js_on_message["location"] = self.location
            js_on_message = json.dumps(js_on_message)
            self.logger.debug("js_on_message {}".format(js_on_message))
            self.mqtt_client.publish(self.topic_prefix + "readings", payload=js_on_message, qos=0, retain=False)
            self.streaming_exit.wait(self.streaming_cycle)

    def _read_sensors(self):
        sensor_reading = {
            "time": int(round(time.time() * 1000)),
            "pressure": round(self.sense.get_pressure(), 3),
            "temperature": {
                "01": round(self.sense.get_temperature(), 3),
                "02": round(self.sense.get_temperature_from_pressure(), 3),
            },
            "humidity": round(self.sense.get_humidity(), 3),
            "acceleration": {
                "x": round(self.sense.get_accelerometer_raw().get("x") * 9.80665, 3),
                "y": round(self.sense.get_accelerometer_raw().get("y") * 9.80665, 3),
                "z": round(self.sense.get_accelerometer_raw().get("z") * 9.80665, 3),
            }
        }
        return sensor_reading

    def start(self):
        if not self.initialized:
            return None
        self.mqtt_client.loop_start()
        self._stream_sensors()


logging.basicConfig(
    filename='/var/log/rpi_broadcaster/rpi_sensehat_mqtt.log',
    format='%(asctime)s.%(msecs)03d %(levelname)s\t[%(name)s] %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger("rpi_sensehat_mqtt")
logger.setLevel(os.environ.get('RPI_SENSEHAT_MQTT_LOGLEVEL', logging.DEBUG))

if __name__ == "__main__":
    # Start RpiSenseHatMqtt app
    logger.info("Starting RpiSenseHatMqtt service")
    root = RpiSenseHatMqtt()
    root.connect()
    logger.info("Run main loop - wait for stop signal")
    root.start()
    logger.info("Stopping main loop")
