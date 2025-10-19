import RPi.GPIO as GPIO
import time

class Shifter:

	def __init__(self, serial, clock, latch):
		self.serialPin = serial
		self.clockPin = clock
		self.latchPin = latch
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(serial, GPIO.OUT)
		GPIO.setup(clock, GPIO.OUT, initial=0) 
		GPIO.setup(latch, GPIO.OUT, initial=0)

	def ping(self, pin):
		GPIO.output(pin, 1) 
		time.sleep(0)
		GPIO.output(pin, 0)

	def shiftByte(self,pattern):
		for i in range(8):
			GPIO.output(self.serialPin, pattern & (1<<i))
			GPIO.output(self.clockPin,1) # ping the clock pin to shift register data
			time.sleep(0)
			GPIO.output(self.clockPin,0)

		GPIO.output(self.latchPin, 1)
		time.sleep(0)
		GPIO.OUTPUT(self.latchPin, 0)

	try:
		while 1: pass
	except:
		GPIO.cleanup()