from sense_hat import SenseHat


sense = SenseHat()
sense.clear()

pressure = sense.get_pressure()
temp = sense.get_temperature()
humidity = sense.get_humidity()
print("pressure {}, temperature {}, humidity {}".format(pressure, temp, humidity))
