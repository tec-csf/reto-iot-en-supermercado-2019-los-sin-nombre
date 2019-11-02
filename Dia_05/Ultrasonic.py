import RPi.GPIO as gpio
import time

class Ultrasonic:
    def __init__(self, trigger, echo):
        gpio.setmode(gpio.BOARD)
        gpio.setwarnings(False)

        self.__TRIGGER = trigger
        self.__ECHO = echo

        gpio.setup(self.__TRIGGER, gpio.OUT)
        gpio.setup(self.__ECHO, gpio.IN)

    def read_distance(self):
        gpio.output(self.__TRIGGER, True)
        
        time.sleep(0.00001)
        gpio.output(self.__TRIGGER, False)
        
        #print('flag')
        
        start_time = time.time()
        stop_time = time.time()
        
        while gpio.input(self.__ECHO) == 0:
            start_time = time.time()
        
        while gpio.input(self.__ECHO) == 1:
            stop_time = time.time()
            
        time_elapsed = stop_time - start_time
        
        distance = (time_elapsed * 34300) / 2
        
        return {'u_distance': distance}
    
if __name__ == '__main__':
    ultrasonic = Ultrasonic()
    while True:
        time.sleep(0.1)
        print(ultrasonic.read_distance())