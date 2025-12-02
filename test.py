import time
import threading
from shifter import Shifter

class Stepper:
    num_steppers = 0
    shifter_outputs = 0
    seq = [0b0001, 0b0011, 0b0010, 0b0110, 0b0100, 0b1100, 0b1000, 0b1001]
    delay = 1200  # microseconds
    steps_per_degree = 4096 / 360

    def __init__(self, shifter, lock, shifter_lock):
        self.s = shifter
        self.angle = 0.0
        self.step_state = 0
        self.busy = False

        self.shifter_bit_start = 4 * Stepper.num_steppers
        self.lock = lock
        self.shifter_lock = shifter_lock

        Stepper.num_steppers += 1

    def __sgn(self, x):
        return 0 if x == 0 else (1 if x > 0 else -1)

    def __step(self, direction):
        self.step_state = (self.step_state + direction) % 8

        with self.shifter_lock:
            mask = ~(0b1111 << self.shifter_bit_start)
            Stepper.shifter_outputs &= mask
            Stepper.shifter_outputs |= Stepper.seq[self.step_state] << self.shifter_bit_start
            self.s.shiftByte(Stepper.shifter_outputs)

        self.angle = (self.angle + direction / Stepper.steps_per_degree) % 360

    def __rotate(self, delta):
        with self.lock:
            self.busy = True
            steps = int(abs(delta) * Stepper.steps_per_degree)
            direction = self.__sgn(delta)

            for _ in range(steps):
                self.__step(direction)
                time.sleep(Stepper.delay / 1e6)

            self.busy = False

    def goAngle(self, target_angle):
        if self.busy:
            return

        delta = (target_angle - self.angle + 180) % 360 - 180
        t = threading.Thread(target=self.__rotate, args=(delta,))
        t.start()

    def zero(self):
        self.angle = 0.0
        self.step_state = 0
