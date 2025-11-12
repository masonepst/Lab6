# stepper_class_shiftregister_multiprocessing.py
#
# Stepper class with multiprocessing support for simultaneous motor control

import time
import multiprocessing
from shifter import Shifter  # your custom Shifter class

class Stepper:
    """
    Controls a stepper motor using a shared shift register.
    Supports multiple motors operating simultaneously via multiprocessing.
    Each motor controls its own 4-bit slice of the shift register.
    """

    # Class constants
    seq = [0b0001, 0b0011, 0b0010, 0b0110, 0b0100, 0b1100, 0b1000, 0b1001]  # 8-step half-step sequence
    delay = 1200  # microseconds between steps
    steps_per_degree = 4096 / 360  # steps per degree for 28BYJ-48

    # Track how many motors have been created
    num_steppers = 0

    def __init__(self, shifter, lock, shifter_outputs):
        self.s = shifter
        self.lock = lock
        self.shifter_outputs = shifter_outputs  # shared memory
        self.angle = multiprocessing.Value('d', 0.0)  # current angle
        self.step_state = 0
        self.shifter_bit_start = 4 * Stepper.num_steppers  # 4 bits per motor
        Stepper.num_steppers += 1

    def __sgn(self, x):
        return 0 if x == 0 else int(abs(x) / x)

    def __step(self, dir):
        self.step_state = (self.step_state + dir) % 8

        with self.lock:
            val = self.shifter_outputs.value
            mask = ~(0b1111 << self.shifter_bit_start)  # clear this motor's 4 bits
            val &= mask
            val |= Stepper.seq[self.step_state] << self.shifter_bit_start  # set new bits
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

    def goAngle(self, angle):
        diff = angle - self.angle.value
        move = (diff + 180) % 360 - 180  # shortest path
        p = multiprocessing.Process(target=self.__rotate, args=(move,))
        p.start()

    def zero(self):
        self.angle.value = 0


# Example usage
if __name__ == '__main__':
    s = Shifter(data=16, latch=20, clock=21)  # GPIO pins for shift register
    lock = multiprocessing.Lock()
    shifter_outputs = multiprocessing.Value('i', 0)  # shared 32-bit integer

    # Create two motors
    m1 = Stepper(s, lock, shifter_outputs)
    m2 = Stepper(s, lock, shifter_outputs)

    # Reset angles
    m1.zero()
    m2.zero()

    # Simultaneous movement
    m1.goAngle(90)
    m2.goAngle(-90)

    # Continue doing other things while motors move
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print('\nend')