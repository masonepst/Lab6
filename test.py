# stepper_class_shiftregister_multiprocessing.py

import time
import multiprocessing
from shifter import Shifter  # your custom Shifter class

class Stepper:
    """
    Controls a stepper motor using a shared shift register.
    Supports multiple motors operating simultaneously via multiprocessing.
    Each motor controls its own 4-bit slice of the shift register.
    """

    seq = [0b0001, 0b0011, 0b0010, 0b0110, 0b0100, 0b1100, 0b1000, 0b1001]
    delay = 1200  # microseconds between steps
    steps_per_degree = 4096 / 360
    num_steppers = 0

    def __init__(self, shifter, lock, shifter_outputs):
        self.s = shifter
        self.lock = lock
        self.shifter_outputs = shifter_outputs
        self.angle = multiprocessing.Value('d', 0.0)  # shared angle
        self.step_state = 0
        self.shifter_bit_start = 4 * Stepper.num_steppers
        Stepper.num_steppers += 1

    def __sgn(self, x):
        return 0 if x == 0 else int(abs(x) / x)

    def __step(self, dir):
        self.step_state = (self.step_state + dir) % 8

        with self.lock:
            val = self.shifter_outputs.value
            mask = ~(0b1111 << self.shifter_bit_start)
            val &= mask
            val |= Stepper.seq[self.step_state] << self.shifter_bit_start
            self.shifter_outputs.value = val
            self.s.shiftByte(val)

        self.angle.value = (self.angle.value + dir / Stepper.steps_per_degree) % 360

    def __rotate(self, delta):
        num_steps = int(Stepper.steps_per_degree * abs(delta))
        dir = self.__sgn(delta)
        for _ in range(num_steps):
            self.__step(dir)
            time.sleep(Stepper.delay / 1e6)

    def rotate(self, delta):
        p = multiprocessing.Process(target=self.__rotate, args=(delta,))
        p.start()

    def goAngle(self, target_angle):
        """
        Rotate to the target angle using the shortest path.
        """
        current = self.angle.value
        delta = (target_angle - current + 180) % 360 - 180  # shortest path
        p = multiprocessing.Process(target=self.__rotate, args=(delta,))
        p.start()

    def zero(self):
        self.angle.value = 0


# Example usage
if __name__ == '__main__':
    s = Shifter(data=16, latch=20, clock=21)
    lock = multiprocessing.Lock()
    shifter_outputs = multiprocessing.Value('i', 0)

    m1 = Stepper(s, lock, shifter_outputs)
    m2 = Stepper(s, lock, shifter_outputs)

    # Demonstration sequence
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