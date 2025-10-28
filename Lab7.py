import socket


led = [0,0,0]

s = socket.socket()

s.bind(('0.0.0.0', 80))
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

while True:

	conn, addr = s.accept()
	request = conn.recv(1024).decode()
	data = parsePOSTdata(request)
	s1 = data['led1']
	s2 = data['led2']
	s3 = data['led3']

	led = [s1, s2, s3]

	html = f"""<!DOCTYPE html>
<html>
<body>
  <h2>LED Brightness Control</h2>
  <form method="POST">
    <label>LED 1:</label>
    <input type="range" name="led1" min="0" max="100" value="{led[0]}"><br>
    <label>LED 2:</label>
    <input type="range" name="led2" min="0" max="100" value="{led[1]}"><br>
    <label>LED 3:</label>
    <input type="range" name="led3" min="0" max="100" value="{led[2]}"><br><br>
    <input type="submit" value="Change Brightness">
  </form>
</body>
</html>"""

	conn.send(b"HTTP/1.1 200 OK\r\n")
	conn.send(b"Content-Type: text/html\r\n")
	conn.send(b"Connection: close\r\n\r\n")

	# body:
	conn.sendall(html.encode()) #Change to LED stuff
	conn.close()
