class RF:
    """docstring for RF"""
    def read_tag(self):
        import RPi.GPIO as GPIO
        import sys

        sys.path.append('/home/pi/Documents/objetos/MFRC522-python')
        from mfrc522 import SimpleMFRC522

        reader = SimpleMFRC522()

        print("Hold tag near the reader")

        try:
            t_id, text= reader.read_no_block()
            return t_id, text

        finally:
            GPIO.cleanup()
            
if __name__ == '__main__':            
    rf = RF()
    rf.readTag()
