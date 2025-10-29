import socket
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

pins = [5,6,26]

led = [0,0,0]
number = 0
pwms = []

for i in range(len(pins)):
	GPIO.setup(pins[i], GPIO.OUT)
	pwm = GPIO.PWM(pins[i], 100)
	pwm.start(0)
	pwms.append(pwm)


s = socket.socket()


s.bind(('0.0.0.0', 8080))
s.listen(1)

def parsePOSTdata(data):
	data_dict = {}
	idx = data.find('\r\n\r\n')+4
	data = data[idx:]
	data_pairs = data.split('&')
	for pair in data_pairs:
		key_val = pair.split('=')
		if len(key_val) == 2:
			data_dict[key_val[0]] = key_val[1]
	return data_dict

try:
	while True:

		conn, addr = s.accept()

		data = parsePOSTdata(conn.recv(1024).decode())

		if 'led' in data and 'brightness' in data:
			number = int(data['led'])
			led[number] = int(data['brightness'])
			pwms[number].ChangeDutyCycle(led[number])


		html = f"""<!DOCTYPE html>
	<html>
	<body>
	  <h2>Brightness level:</h2>
	  <form method="POST">
	    <input type="range" name="brightness" min="0" max="100" value="{led[number]}"><br><br>
	    <b>Select LED:</b><br>
	    <input type="radio" name="led" value="0" 'checked> LED 1 ({led[0]}%)<br>
	    <input type="radio" name="led" value="1" > LED 2 ({led[1]}%)<br>
	    <input type="radio" name="led" value="2" > LED 3 ({led[2]}%)<br><br>
	    <input type="submit" value="Change Brightness">
	  </form>
	</body>
	</html>"""

		conn.send(b"HTTP/1.1 200 OK\r\n")
		conn.send(b"Content-Type: text/html\r\n")
		conn.send(b"Connection: close\r\n\r\n")
		conn.sendall(html.encode())
		conn.close()

except KeyboardInterrupt:
	for i in range(len(LED_pwm)):
		pwms[i].stop()
		GPIO.cleanup()




