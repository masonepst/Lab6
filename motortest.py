import socket
import threading
from test import Stepper, Shifter
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.OUT)

s = Shifter(data=16, latch=20, clock=21)

shifter_lock = threading.Lock()
lock1 = threading.Lock()
lock2 = threading.Lock()

m1 = Stepper(s, lock1, shifter_lock)
m2 = Stepper(s, lock2, shifter_lock)

m1.zero()
m2.zero()
motor1 = 0
motor2 = 0

sock = socket.socket()
sock.bind(('0.0.0.0', 8080))
sock.listen(1)

def parsePOSTdata(data):
    data_dict = {}
    idx = data.find('\r\n\r\n') + 4
    data = data[idx:]
    for pair in data.split('&'):
        if '=' in pair:
            key, val = pair.split('=')
            data_dict[key] = val
    return data_dict

try:
    while True:
        conn, addr = sock.accept()
        data = parsePOSTdata(conn.recv(1024).decode())

        if 'motor1' in data and 'motor2' in data:
            motor1 = float(data['motor1'])
            motor2 = float(data['motor2'])

            t1 = threading.Thread(target=m1.goAngle, args=(motor1,))
            t2 = threading.Thread(target=m2.goAngle, args=(motor2,))
            t1.start()
            t2.start()

        if "laser" in data:
            GPIO.output(25, GPIO.HIGH if data["laser"] == "on" else GPIO.LOW)

        print(f"M1 angle: {m1.angle:.2f} | Requested: {motor1}")
        print(f"M2 angle: {m2.angle:.2f} | Requested: {motor2}")

        html = f"""<!DOCTYPE html>
<html>
<body>
  <h2>Laser Control</h2>
  <form method="POST">
    <label>Motor 1 Angle:</label><br>
    <input type="number" name="motor1" min="0" max="360" value="{motor1}" step="1"><br><br>
    <label>Motor 2 Angle:</label><br>
    <input type="number" name="motor2" min="0" max="360" value="{motor2}" step="1"><br><br>
    <input type="submit" value="Move Laser">
  </form>
  <hr>
  <h3>Laser Power</h3>
  <form method="POST">
    <button name="laser" value="on" style="width:120px;height:40px;">Turn ON</button>
    <button name="laser" value="off" style="width:120px;height:40px;">Turn OFF</button>
  </form>
</body>
</html>
"""
        conn.send(b"HTTP/1.1 200 OK\r\n")
        conn.send(b"Content-Type: text/html\r\n")
        conn.send(b"Connection: close\r\n\r\n")
        conn.sendall(html.encode())
        conn.close()

except KeyboardInterrupt:
    print("Shutting down gracefully.")
    sock.close()
    GPIO.cleanup()
