import RPi.GPIO as io
import time
class Buzzer:
    def __init__(self, physical_pin):
        self.__pin = physical_pin
        io.setwarnings(False)
        io.setmode(io.BOARD)
        io.setup(self.__pin, io.OUT)
        
    def buzz(self, seconds):
        io.output(self.__pin, io.HIGH)
        
        time.sleep(seconds)
        
        io.output(self.__pin, io.LOW)
        
if __name__ == '__main__':
    b = Buzzer(13)
    b.buzz(seconds=0.5)