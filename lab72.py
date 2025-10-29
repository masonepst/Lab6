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
<head>
  <meta charset="UTF-8">
  <title>LED Brightness Control</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 40px;
    }}
    .led {{
      margin-bottom: 20px;
    }}
    label {{
      display: inline-block;
      width: 60px;
    }}
    input[type=range] {{
      width: 200px;
      vertical-align: middle;
    }}
    span {{
      display: inline-block;
      width: 30px;
      text-align: right;
    }}
  </style>
</head>
<body>
  <h2>LED Brightness Control</h2>

  <div class="led">
    <label>LED1</label>
    <input type="range" min="0" max="100" value="{led[0]}" id="led0">
    <span id="val0">{led[0]}</span>
  </div>

  <div class="led">
    <label>LED2</label>
    <input type="range" min="0" max="100" value="{led[1]}" id="led1">
    <span id="val1">{led[1]}</span>
  </div>

  <div class="led">
    <label>LED3</label>
    <input type="range" min="0" max="100" value="{led[2]}" id="led2">
    <span id="val2">{led[2]}</span>
  </div>

  <script>
    // Function to send brightness updates to the server
    function sendUpdate(led, brightness) {{
      fetch("/", {{
        method: "POST",
        headers: {{
          "Content-Type": "application/x-www-form-urlencoded"
        }},
        body: "led=" + led + "&brightness=" + brightness
      }});
    }}

    // Attach event listeners for all sliders
    for (let i = 0; i < 3; i++) {{
      const slider = document.getElementById("led" + i);
      const valSpan = document.getElementById("val" + i);
      slider.addEventListener("input", () => {{
        valSpan.textContent = slider.value;
        sendUpdate(i, slider.value);
      }});
    }}
  </script>
</body>
</html>"""


		conn.send(b"HTTP/1.1 200 OK\r\n")
		conn.send(b"Content-Type: text/html\r\n")
		conn.send(b"Connection: close\r\n\r\n")
		conn.sendall(html.encode())
		conn.close()

except KeyboardInterrupt:
	for i in range(len(pwms)):
		pwms[i].stop()
		GPIO.cleanup()





