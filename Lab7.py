import socket


led = [0,0,0]
select = 0

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

	method = request.split(' ')[0]

	if method == 'POST':
    data = parsePOSTdata(request)
    if 'led' in data and 'brightness' in data:
        select = int(data['led'])
        led[select] = int(data['brightness'])

		led = [s1, s2, s3]

	html = f"""<!DOCTYPE html>
<html>
<body>
  <h2>Brightness level:</h2>
  <form method="POST">
    <input type="range" name="brightness" min="0" max="100" value="{led[select]}"><br><br>
    <b>Select LED:</b><br>
    <input type="radio" name="led" value="0" {'checked' if select == 0 else ''}> LED 1 ({led[0]}%)<br>
    <input type="radio" name="led" value="1" {'checked' if select == 1 else ''}> LED 2 ({led[1]}%)<br>
    <input type="radio" name="led" value="2" {'checked' if select == 2 else ''}> LED 3 ({led[2]}%)<br><br>
    <input type="submit" value="Change Brightness">
  </form>
</body>
</html>"""

	conn.send(b"HTTP/1.1 200 OK\r\n")
	conn.send(b"Content-Type: text/html\r\n")
	conn.send(b"Connection: close\r\n\r\n")
	conn.sendall(html.encode())
	conn.close()
