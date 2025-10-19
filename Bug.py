import RPi.GPIO as GPIO
import time
from bug_class import Bug

# GPIO pins
s1 = 5
s2 = 6
s3 = 26

GPIO.setmode(GPIO.BCM)
GPIO.setup(s1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(s2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(s3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

bug = Bug()
s2_last = GPIO.input(s2)
s3_last = GPIO.input(s3)

try:
    while True:
        # Start/stop bug safely
        if GPIO.input(s1):
            bug.start()
        else:
            bug.stop()

        # Toggle wrap mode on s2 change (debounced)
        s2_now = GPIO.input(s2)
        if s2_now == 1 and s2_last == 0:
            bug.isWrapOn = not bug.isWrapOn
        s2_last = s2_now

        # Adjust timestep once per press of s3
        s3_now = GPIO.input(s3)
        if s3_now == 1 and s3_last == 0:
            bug.timestep = bug.timestep / 3
        s3_last = s3_now

        # Short delay to reduce CPU usage and debounce
        time.sleep(0.05)

except KeyboardInterrupt:
    GPIO.cleanup()
    bug.stop()
