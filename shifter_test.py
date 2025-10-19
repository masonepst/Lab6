from shifter import Shifter
import time
import random
import RPi.GPIO as GPIO

test = Shifter(serial = 23, clock = 25, latch = 24)

x = 0
timestep = 0.05
try:
	while True:
		pattern = 1 << x
		test.shiftByte(pattern)

		walk = random.choice([-1,1])
		x += walk

		if x < 0:
			x = 0
		elif x > 7:
			x = 7


	time.sleep(timestep)

except KeyboardInterrupt:
	GPIO.cleanup()