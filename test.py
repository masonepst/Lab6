import time
import multiprocessing
from shifter import Shifter

class Stepper:
    num_steppers = 0
    shifter_outputs = multiprocessing.Value('i', 0)  # shared, synchronized integer
    seq = [0b0001,0b0011,0b0010,0b0110,0b0100,0b1100,0b1000,0b1001]
    delay = 3000
    steps_per_degree = 4096/360

    def __init__(self, shifter, local_lock, hw_lock):
        self.s = shifter
        self.angle = multiprocessing.Value('d', 0.0)
        self.step_state = 0
        self.shifter_bit_start = 4 * Stepper.num_steppers
        self.local_lock = local_lock
        self.hw_lock = hw_lock
        Stepper.num_steppers += 1

    def __sgn(self, x):
        if x == 0: return 0
        else: return int(abs(x)/x)

    def __step(self, dir):
        self.step_state = (self.step_state + dir) % 8
        with self.hw_lock:  # protect shift register hardware access
            bitmask = ~(0b1111 << self.shifter_bit_start)
            Stepper.shifter_outputs.value &= bitmask
            Stepper.shifter_outputs.value |= Stepper.seq[self.step_state] << self.shifter_bit_start
            self.s.shiftByte(Stepper.shifter_outputs.value)
        self.angle.value = (self.angle.value + dir / Stepper.steps_per_degree) % 360

    def __rotate(self, delta):
        self.local_lock.acquire()
        numSteps = int(Stepper.steps_per_degree * abs(delta))
        dir = self.__sgn(delta)
        for _ in range(numSteps):
            self.__step(dir)
            time.sleep(Stepper.delay / 1e6)
        self.local_lock.release()

    def rotate(self, delta):
        p = multiprocessing.Process(target=self.__rotate, args=(delta,))
        p.start()

    def goAngle(self, angle):
        dif = angle - self.angle.value
        move = (dif + 180) % 360 - 180
        p = multiprocessing.Process(target=self.__rotate, args=(move,))
        p.start()

    def zero(self):
        self.angle.value = 0


if __name__ == '__main__':
    s = Shifter(data=16, latch=20, clock=21)

    hw_lock = multiprocessing.Lock()  # shared hardware access lock
    lock1 = multiprocessing.Lock()    # per-motor logic lock
    lock2 = multiprocessing.Lock()

    m1 = Stepper(s, lock1, hw_lock)
    m2 = Stepper(s, lock2, hw_lock)

    m1.zero()
    m2.zero()

 
    m1.zero()
    m2.zero()
    m1.goAngle(90)
    m1.goAngle(-45)
    m2.goAngle(-90)
    m2.goAngle(45)
    m1.goAngle(-135)
    m1.goAngle(135)
    m1.goAngle(0)

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print('\nend')
