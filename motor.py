import socket
import multiprocessing
from lab8 import Stepper, Shifter
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(25,GPIO.OUT)

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


        if 'motor1' in data and 'motor2' in data:
            motor1 = float(data['motor1'])
            motor2 = float(data['motor2'])
            m1.goAngle(motor1)
            m2.goAngle(motor2)


        if "laser" in data:
            if data["laser"] == "on":
                GPIO.output(25, GPIO.HIGH)
            else:
                GPIO.output(25, GPIO.LOW)

        print("M1 angle before move:", m1.angle.value)
        print("Requested:", motor1)
        print("M2 angle before move:", m2.angle.value)
        print("Requested:", motor2)



        html = f"""<!DOCTYPE html>
<html>
<body>
  <h2>Laser Control</h2>

  <form method="POST">
    <label>Motor 1 Angle:</label><br>
    <input type="range" name="motor1" min="0" max="360" value="{motor1}">
    <br><br>

    <label>Motor 2 Angle:</label><br>
    <input type="range" name="motor2" min="0" max="360" value="{motor2}">
    <br><br>

    <input type="submit" value="Move Laser">
  </form>

  <hr>

  <h3>Laser Power</h3>
  <form method="POST">
    <button name="laser" value="on" style="width:120px;height:40px;">Turn ON</button>
    <button name="laser" value="off" style="width:120px;height:40px;">Turn OFF</button>
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
