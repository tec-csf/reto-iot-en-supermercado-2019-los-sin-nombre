import RPi.GPIO as gpio
import time

class ADC:
    def __init__(self, pins_inputs):
        if max(pins_inputs) >= 6:
            raise RuntimeError("Can't have an input higher than 6.")
        self.__a_pin = 16
        self.__b_pin = 18
        self.__c_pin = 32
        self.__adc_inputs = pins_inputs
        self.addresses = [self.__decimal_to_binary(dec, 3) for dec in pins_inputs.keys()]
        self.__outputs_pins = {
            1: 29,
            2: 31,
            3: 33,
            4: 35,
            5: 37,
            6: 36,
            7: 38,
            8: 40
        }
        
    def __decimal_to_binary(self, dec, n):
        binstr = bin(dec).split("0b")[1]
        return ("".join(["0"]*(n - len(binstr))) + binstr)
        
    def __address_pin(self, pin, bit):
        gpio.setwarnings(False)
        gpio.setmode(gpio.BOARD)
        gpio.setup(pin, gpio.OUT)
        if bit=='1':
            gpio.output(pin, gpio.HIGH)
        elif bit=='0':
            gpio.output(pin, gpio.LOW)
            
    def __a(self, bit):
        self.__address_pin(self.__a_pin, bit)
    def __b(self, bit):
        self.__address_pin(self.__b_pin, bit)
    def __c(self, bit):
        self.__address_pin(self.__c_pin, bit)
        
    def __set_address(self, address):
        self.__a(address[0])
        self.__b(address[1])
        self.__c(address[2])
        
    def __read_input(self, pin):
        gpio.setwarnings(False)
        gpio.setmode(gpio.BOARD)
        gpio.setup(pin, gpio.IN, pull_up_down=gpio.PUD_DOWN)
        return gpio.input(pin)
        
    def read_addresses(self):
        bi_readings = {}
        for address in self.addresses:
            self.__set_address(address)
            time.sleep(0.2)
            bi_readings.setdefault(address, "".join([str(self.__read_input(output_pin)) for _, output_pin in self.__outputs_pins.items()]))
        return bi_readings, {self.__adc_inputs[int(key, 2)]: int(val, 2) for key, val in bi_readings.items()}
    
if __name__ == "__main__":
    adc = ADC([0])
    while True:
        time.sleep(0.1)
        print(adc.read_addresses())