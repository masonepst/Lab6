import time
import multiprocessing
from shifter import Shifter

class Stepper:
    num_steppers = 0
    shifter_outputs = multiprocessing.Value('i', 0)
    seq = [0b0001,0b0011,0b0010,0b0110,0b0100,0b1100,0b1000,0b1001]
    delay = 1200
    steps_per_degree = 4096/360

    def __init__(self, shifter, lock, newlock):
        self.s = shifter
        self.angle = multiprocessing.Value('d', 0.0)     # current angle
        self.step_state = multiprocessing.Value('i', 0)
        self.lock = lock
        self.newlock = newlock

        # Queue for target angles
        self.target_queue = multiprocessing.Queue()

        # Start the worker process
        self.process = multiprocessing.Process(target=self._worker)
        self.process.daemon = True
        self.process.start()

        self.shifter_bit_start = 4 * Stepper.num_steppers
        Stepper.num_steppers += 1

    def __sgn(self, x):
        if x == 0:
            return 0
        return 1 if x > 0 else -1

    def __step(self, dir):
        with self.newlock:
            # update step state
            self.step_state.value = (self.step_state.value + dir) % 8
            mask = ~(0b1111 << self.shifter_bit_start)
            Stepper.shifter_outputs.value &= mask
            Stepper.shifter_outputs.value |= Stepper.seq[self.step_state.value] << self.shifter_bit_start
            self.s.shiftByte(Stepper.shifter_outputs.value)

        # update angle
        self.angle.value = (self.angle.value + dir / Stepper.steps_per_degree) % 360

    def _worker(self):
        while True:
            target_angle = self.target_queue.get()  # blocks until new angle arrives
            delta = ((target_angle - self.angle.value + 180) % 360) - 180
            direction = self.__sgn(delta)
            steps = int(abs(delta) * Stepper.steps_per_degree)
            for _ in range(steps):
                self.__step(direction)
                time.sleep(Stepper.delay / 1e6)

    def goAngle(self, angle):
        # push angle into the queue
        self.target_queue.put(angle)

    def zero(self):
        self.angle.value = 0
        self.step_state.value = 0




# Example use:

if __name__ == '__main__':

    s = Shifter(data=16,latch=20,clock=21)   # set up Shifter

    # Use multiprocessing.Lock() to prevent motors from trying to 
    # execute multiple operations at the same time:
    newlock = multiprocessing.Lock()
    lock1 = multiprocessing.Lock()
    lock2 = multiprocessing.Lock()

    # Instantiate 2 Steppers:
    m1 = Stepper(s, lock1, newlock)
    m2 = Stepper(s, lock2, newlock)


    m1.zero()
    m2.zero()
    m1.goAngle(90)
    m1.goAngle(-45)
    m2.goAngle(-90)
    m2.goAngle(45)
    m1.goAngle(-135)
    m1.goAngle(135)
    m1.goAngle(0)
 
    # While the motors are running in their separate processes, the main
    # code can continue doing its thing: 
    try:
        while True:
            pass
    except:
        print('\nend')