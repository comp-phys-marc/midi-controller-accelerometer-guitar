import RPi.GPIO as gpio
import time

pin = 38

gpio.setmode(gpio.BOARD)
gpio.setup(pin, gpio.OUT)

gpio.output(pin, gpio.HIGH)
time.sleep(1)
gpio.output(pin, gpio.LOW)
time.sleep(1)
gpio.output(pin, gpio.HIGH)
time.sleep(1)
gpio.output(pin, gpio.LOW)

gpio.cleanup()
