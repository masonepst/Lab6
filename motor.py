import socket
import multiprocessing
from lab8 import Stepper, Shifter

s = Shifter(data=16,latch=20,clock=21)

newlock = multiprocessing.Lock()
lock1 = multiprocessing.Lock()
lock2 = multiprocessing.Lock()

m1 = Stepper(s, lock1, newlock)
m2 = Stepper(s, lock2, newlock)

m1.zero()
m2.zero()


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

        motor1 = 0
        motor2 = 0

        if 'motor1' in data and 'motor2' in data:
            motor1 = float(data['motor1'])
            motor2 = float(data['motor2'])
            m1.goAngle(motor1)
            m2.goAngle(motor2)

        html = f"""<!DOCTYPE html>
<html>
<body>
  <h2>Laser Control</h2>
  <form method="POST">
    <label>Motor 1 Angle:</label><br>
    <input type="range" name="angle1" min="0" max="360" value="{motor1}"><br><br>
    <label>Motor 2 Angle:</label><br>
    <input type="range" name="angle2" min="0" max="360" value="{motor2}"><br><br>
    <input type="submit" value="Move Laser">
  </form>
</body>
</html>"""
        conn.send(b"HTTP/1.1 200 OK\r\n")
        conn.send(b"Content-Type: text/html\r\n")
        conn.send(b"Connection: close\r\n\r\n")
        conn.sendall(html.encode())
        conn.close()

except KeyboardInterrupt:
    print("KeyboardInterrupt")
