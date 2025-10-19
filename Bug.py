from bug_class import Bug
import RPi.GPIO as GPIO
import time

s1 = 5
s2 = 6
s3 = 26
GPIO.setmode(GPIO.BCM)
GPIO.setup(s1, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(s2, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(s3, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

bug = Bug()
s2_last = GPIO.input(s2)
try:
	while True:
		if GPIO.input(s1) == 1:
			bug.start()
		else:
			bug.stop()
		s2_now = GPIO.input(s2)
		if s2_now != s2_last:
			if bug.isWrapOn == True:
				bug.isWrapOn = False
			else:
				bug.isWrapOn = True

		if GPIO.input(s3) == 1:
			bug.timestep = bug.timestep/3

		time.sleep(0.01)
except KeyboardInterrupt:
	GPIO.cleanup()



