from shifter import Shifter
import time
import random
import RPi.GPIO as GPIO

test = Shifter(serial = 23, clock = 25, latch = 24)

led = 0

try:
	while True:
		pattern = 1 << led
		test.shiftByte(pattern)

		walk = random.choice([-1,1])
		led += walk

		if led < 0:
			led = 0
		elif led > 7:
			led = 7


	time.slee(0.05)

except KeyboardInterrupt:
	GPIO.cleanup()