import RPi.GPIO as gpio
import Adafruit_DHT
import time

from adc import ADC

class Presion(object):
    """docstring for Presion"""
    def __init__(self, address):
        self.adc = ADC([address])

    def read_sensor(self):
        return self.adc.read_addresses()

def binaryToTemperature(num):
    b = int(num, 2)
    vol = b * 6 / 255
    temperature = vol * 150 / 6
    return temperature

if __name__ == "__main__":
    presion = Presion(0)
    
    while True:
        time.sleep(1)
        print(presion.read_sensor())
         