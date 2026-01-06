import spidev
import time

CE0 = 24
CE1 = 26
MOSI = 19
MISO = 21
SCLK = 23

# Open SPI bus 0, device (CS) 0
spi = spidev.SpiDev()
spi.open(0, 0)

# Set SPI speed and mode
spi.max_speed_hz = 5000
spi.mode = 0

try:
	for _ in range(20):
		read_one = spi.xfer2([11])
		time.sleep(1)
		print(read_one[0])

except Exception as e:
	print(str(e))
	spi.close()
