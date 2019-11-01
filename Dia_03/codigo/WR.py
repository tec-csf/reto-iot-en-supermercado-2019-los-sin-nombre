class WR(object):
    def read_write(self):
        import RPi.GPIO as GPIO
        import sys
        sys.path.append('/home/pi/Documents/objetos/MFRC522-python')
        from mfrc522 import SimpleMFRC522
        reader = SimpleMFRC522()
        try:
            text = input('Your Name: ')
            print("Now place tag next to the scanner to write")
            id, text = reader.write(text)
            print("recorded")
            print(id)
            print(text)
               
        finally:
             GPIO.cleanup()

if __name__ == '__main__':
    wr = WR()
    wr.read_write()