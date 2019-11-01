import time
import RPi.GPIO as io

class Puerta:
    """docstring for Puerta"""
    def __init__(self, physical_pin):
        self.pin = physical_pin
        

    def read_door(self):
        io.setmode(io.BOARD)
        io.setup(self.pin, io.IN, pull_up_down=io.PUD_UP)
        if io.input(self.pin) == io.HIGH:
            return True
        else:
            return False

def main():
    puerta = Puerta(7)

    while True:
        time.sleep(1)
        print(puerta.read_door())

if __name__ == '__main__':
    main()