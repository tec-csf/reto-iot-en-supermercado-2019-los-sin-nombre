import RPi.GPIO as GPIO
import time
import threading
import subprocess
import requests
import Adafruit_DHT
from pprint import pprint
import sys
import time
from Proximity import Proximity
from Presion import Presion
from puerta import Puerta
from Ultrasonic import Ultrasonic
from adc import ADC
from RF import RF
from WR import WR
import json

#RF.readTag()
#WR.read_Write()
def readADC():
    adc = ADC([0])
    return adc.read_addresses()

def faceRecognition():
    GPIO.setwarnings(False) # Ignore warning for now
    GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
                    
    subprocess.call(['fswebcam -r 640x480 --no-banner /home/pi/Desktop/image.jpg', '-1'], shell=True)

    #Azure
    face_uri = "https://raspberrycp.cognitiveservices.azure.com/vision/v1.0/analyze?visualFeatures=Faces&language=en"
    pathToFileInDisk = r'/home/pi/Desktop/image.jpg'
    with open( pathToFileInDisk, 'rb' ) as f:
        data = f.read()
        
    headers = { "Content-Type": "application/octet-stream" ,'Ocp-Apim-Subscription-Key': '7e9cfbb244204fb994babd6111235269'}
    response = requests.post(face_uri, headers=headers, data=data)
    faces = response.json()
    return faces;

def binaryToTemperature(num):
    b = int(num, 2)
    vol = b * 6 / 255
    temperature = vol * 150 / 6
    return temperature
def temp():
    sensor = Adafruit_DHT.DHT11
    pin=22
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    
    if humidity is not None and temperature is not None:
        return {'temperature': temperature, 'humidity':humidity}
        #print('Temp={0:0.1f}°C  Humidity={1:0.1f}%'.format(temperature, humidity))
    else:
        #print('Failed to get reading. Try again!')
        return {'temperature': None, 'humidity': None}
    
def get_data_dict(adc_inputs):
    adc = ADC(adc_inputs)
    data_dict = get_time_dict()
    data_dict.update(temp())
    _, adc_dict = adc.read_addresses()
    data_dict.update(adc_dict)
    ultrasonic = Ultrasonic(trigger=3, echo=5)
    data_dict.update(ultrasonic.read_distance())
    return data_dict

def get_time_dict():
    return {'ts': int(time.time())}

def captureInfoCam():
    GPIO.setwarnings(False) # Ignore warning for now
    GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
                    
    subprocess.call(['fswebcam -r 640x480 --no-banner /home/pi/Desktop/image.jpg', '-1'], shell=True)

    #Azure
    face_uri = "https://raspberrycp.cognitiveservices.azure.com/vision/v1.0/analyze?visualFeatures=Faces&language=en"
    pathToFileInDisk = r'/home/pi/Desktop/image.jpg'
    with open( pathToFileInDisk, 'rb' ) as f:
        data = f.read()
        
    headers = { "Content-Type": "application/octet-stream" ,'Ocp-Apim-Subscription-Key': '7e9cfbb244204fb994babd6111235269'}
    
    try:
        response = requests.post(face_uri, headers=headers, data=data)
        faces = response.json()
        
        #pprint(faces)
        age = faces['faces'][0].get('age')
        gender = faces['faces'][0].get('gender')
        
        datosUsuario = [age, gender]
    except requests.exceptions.ConnectionError:
        return None
    except IndexError:
        return None
    else:
        return datosUsuario

def get_tag_info():
    rf = RF()
    t_id, nameP = rf.read_tag()
    if t_id != None:
        datos = captureInfoCam()
        timest = int(time.time())
        
        if datos == None:
            return {'ts': timest, 'product_id': t_id, 'type_id': nameP ,'gender': None, 'age': None}
        
        return {'ts': timest, 'product_id': t_id, 'type_id': nameP ,'gender': datos[1], 'age': datos[0]}

puerta = Puerta(7)

while True:
    
    adc_inputs = {
        0: 'Peso_P1',
        2: 'Peso_P2'
    }
    
    if puerta.read_door():
        print("Puerta cerrada: ", end='')
        print(get_data_dict( adc_inputs ))
    else:
        print("Puerta abierta: ", end='')
        print(get_tag_info())
        
    
    