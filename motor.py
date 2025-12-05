import socket
import multiprocessing
from lab8 import Stepper, Shifter
import RPi.GPIO as GPIO
from Project import JSON_pull
import math
import time
from Project import my_turret_distances

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
motor1 = 0
motor2 = 0

sock = socket.socket()
sock.bind(('0.0.0.0', 8080))
sock.listen(1)

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

turrets, globes = JSON_pull()
dist_globes, dist_turrets = my_turret_distances(turrets, globes)

for stud_id, (dist_r, dist_theta) in dist_turrets.items():
    print(f"turret {stud_id}: delta r = {dist_r:.2f}, delta theta = {dist_theta:.2f} degrees")

for (dist_r, dist_theta, dist_z) in dist_globes:

    print(f"delta r = {dist_r:.2f}, delta theta = {dist_theta:.2f} degrees, delta z = {dist_z:.2f}")

while True:
    conn, addr = sock.accept()
    data = parsePOSTdata(conn.recv(1024).decode())

    if "start" in data:
        print("starting")

        motor1 = 0
        motor2 = 0

    # motor1 is bottom and motor 2 is laser
        for stud_id, (dist_r, dist_theta) in dist_turrets.items():
            if stud_id == str("7"):
                continue
                
            time.sleep(2)
            GPIO.output(25,GPIO.LOW)
            motor1 = dist_theta
            m1.goAngle(motor1)
            motor2 = 0
            m2.goAngle(motor2) #This should be at point where laser is facing down towards other turrets. No need for z actuation
            GPIO.output(25, GPIO.HIGH)
            time.sleep(2)

        for (dist_r, dist_theta, dist_z) in dist_globes:
            time.sleep(2)
            GPIO.output(25,GPIO.LOW)
            motor2 = math.degrees(math.atan2(dist_z, dist_r))
            motor1 = dist_theta
            m1.goAngle(motor1)
            m2.goAngle(motor2)
            GPIO.output(25, GPIO.HIGH)
            time.sleep(2)

        GPIO.output(25,GPIO.LOW)
        print("Done")


    #if 'motor1' in data:
     #   motor1 = float(data['motor1'])
     #   m1.goAngle(motor1) #motor 1 and 2 value will be calculated based on the distances of turrets and globes

    #if 'motor2' in data:
    #    motor2 = float(data['motor2'])
    #    m2.goAngle(motor2)



    #if "laser" in data:
     #   if data["laser"] == "on":
      #      GPIO.output(25, GPIO.HIGH)
       # else:
        #    GPIO.output(25, GPIO.LOW)


    html = f"""<!DOCTYPE html>
<html>
<body>
  <h2>Laser Turret Control</h2>

  <form method="POST">
    <button name="start" value="go" style="width:160px;height:50px;font-size:18px;">
      START SWEEP
    </button>
  </form>

</body>
</html>
"""
    conn.send(b"HTTP/1.1 200 OK\r\n")
    conn.send(b"Content-Type: text/html\r\n")
    conn.send(b"Connection: close\r\n\r\n")
    conn.sendall(html.encode())
    conn.close()

