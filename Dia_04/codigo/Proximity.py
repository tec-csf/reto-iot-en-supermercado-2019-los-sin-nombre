import RPi.GPIO as io
import time

class Proximity:
    """docstring for Proximity"""
    def __init__(self, pinIN, pinOUT):
        self.pinIN  = pinIN
        self.pinOUT = pinOUT
        io.setmode(io.BCM)
        io.setup(self.pinIN, io.IN)
        io.setup(self.pinOUT, io.OUT)

    def proxFunction(self):
        try:
            time.sleep(2)
            while True:
                if io.input(self.pinIN) == io.HiGH:
                    io.output(self.pinOUT, True)
                    time.sleep(0.5)
                    io.output(self.pinOUT, False)

                    print("Motion detected...")
                    time.sleep(5)

                time.sleep(0.1)
        except:
            io.cleanup()
