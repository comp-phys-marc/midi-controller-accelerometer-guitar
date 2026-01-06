import board
import digitalio
import busio
import time

print("Hello, blinka!")

# Try to create a Digital input
pin = digitalio.DigitalInOut(board.D27)
pin.direction = digitalio.Direction.OUTPUT

pin.value = False
time.sleep(1)
pin.value = True
time.sleep(1)
pin.value = False
time.sleep(1)
pin.value = True

print("Digital IO ok!")

# Try to create an I2C device
i2c = busio.I2C(board.SCL, board.SDA)
print("I2C ok!")

# Try to create an SPI device
spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
print("SPI ok!")

print("done!")
