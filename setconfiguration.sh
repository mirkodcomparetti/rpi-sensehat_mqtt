#!/bin/bash

get_ack() {
	# https://djm.me/ask
	local prompt default reply

	while true; do
		if [ "${2:-}" = "Y" ]; then
			prompt="Y/n"
			default=Y
		elif [ "${2:-}" = "N" ]; then
			prompt="y/N"
			default=N
		else
			prompt="y/n"
			default=
		fi

		# Ask the question (not using "read -p" as it uses stderr not stdout)
		echo -n "$1 [$prompt] "
		# Read the answer (use /dev/tty in case stdin is redirected from somewhere else)
		read reply </dev/tty

		# Default?
		if [ -z "$reply" ]; then
			reply=$default
		fi
		# Check if the reply is valid
		case "$reply" in
			Y*|y*)
				return 0;;
			N*|n*)
				return 1;;
		esac
	done
}

echo "CheckUPS configuration for RevPi";
if [ "$EUID" -ne 0 ]; then
	echo "Please run as root or sudo"
	exit
fi

echo "This script assumes the configuration is saved in the same folder as this script ";
echo "Required files:";
echo "- rpi_sensehat_mqtt.py";
echo "- rpi_sensehat_mqtt.logrotate";
echo "- rpi_sensehat_mqtt.env";
echo "- rpi_sensehat_mqtt.service";

if ! (get_ack "Do you want to continue?" N;) then
	echo "Exiting, bye!";
	exit 0;
fi

restart_service=false;

echo "Moving script files";
if test -f "./rpi_sensehat_mqtt.py"; then
  sudo /bin/chown -R root:root ./rpi_sensehat_mqtt.py
  sudo /bin/mkdir -p /etc/rpi_broadcaster/
  sudo /bin/mv ./sensehat_mqtt.py /etc/rpi_broadcaster/
  restart_service=true;
else
  echo "Script files not present, skip";
fi

echo "Creating log folder for rpi_broadcaster";
if test -d "/var/log/rpi_broadcaster/"; then
  echo "Log folder already present, skip";
else
  sudo /bin/mkdir -p /var/log/rpi_broadcaster/
  restart_service=true;
fi

echo "Moving logrotate files";
if test -f "./rpi_sensehat_mqtt.logrotate"; then
  sudo /bin/chown -R root:root ./rpi_sensehat_mqtt.logrotate
  sudo /bin/mv ./sensehat_mqtt.logrotate /etc/logrotate.d/rpi_sensehat_mqtt
else
  echo "Logrotate files not present, skip";
fi

echo "Moving environment files";
if test -f "./rpi_sensehat_mqtt.env"; then
  sudo /bin/chown -R root:root ./rpi_sensehat_mqtt.env
  sudo /bin/mv ./rpi_sensehat_mqtt.env /etc/default/rpi_sensehat_mqtt
  restart_service=true;
else
  echo "Environment files not present, skip";
fi

echo "Moving service files";
if test -f "./rpi_sensehat_mqtt.service"; then
  sudo /bin/chown -R root:root ./rpi_sensehat_mqtt.service
  sudo /bin/mv ./rpi_sensehat_mqtt.service /lib/systemd/system/rpi_sensehat_mqtt.service
  restart_service=true;
else
  echo "Service files not present, skip";
fi

echo "Reload and reboot service";
if $restart_service; then
  sudo /bin/systemctl daemon-reload
  sudo /bin/systemctl enable rpi_sensehat_mqtt.service
  sudo /bin/systemctl restart rpi_sensehat_mqtt.service
else
  echo "No changes to service related files, skip";
fi

echo "Done";
