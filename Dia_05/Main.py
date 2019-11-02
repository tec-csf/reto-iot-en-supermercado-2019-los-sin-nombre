import RPi.GPIO as GPIO
import time
import threading
import subprocess
import requests
import Adafruit_DHT
from pprint import pprint
import sys
import time
from Buzzer import Buzzer
from Proximity import Proximity
from Presion import Presion
from puerta import Puerta
from Ultrasonic import Ultrasonic
from adc import ADC
from RF import RF
from WR import WR
import json

#imports para cloud
import datetime
import time
import jwt
import paho.mqtt.client as mqtt
import random

#variables para cloud
ssl_private_key_filepath = '/home/pi/Documents/IOT/iot_supermercado/demo_05/demo_private.pem'
ssl_algorithm = 'RS256'  # Either RS256 or ES256
root_cert_filepath = '/home/pi/Documents/IOT/iot_supermercado/demo_05/roots.pem'
project_id = 'iot-semanai'
gcp_location = 'us-central1'
registry_Fridge = 'Fridge_IoT'
registry_Client = 'Client_Info'
device_id = 'Rasp'

sensor_temp = Adafruit_DHT.DHT11

#cloud get current time
cur_time = datetime.datetime.utcnow()

#generate connection with cloud

def create_jwt():
    token = {
        'iat': cur_time,
        'exp': cur_time + datetime.timedelta(minutes=60),
        'aud': project_id
    }

    with open(ssl_private_key_filepath, 'r') as f:
        private_key = f.read()

    return jwt.encode(token, private_key, ssl_algorithm)


# _CLIENT_ID = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(
#     project_id, gcp_location, registry_id, device_id)
# _MQTT_TOPIC = '/devices/{}/events'.format(device_id)

# client = mqtt.Client(client_id=_CLIENT_ID)
# authorization is handled purely with JWT, no user/pass, so username can be whatever

def error_str(rc):
    return '{}: {}'.format(rc, mqtt.error_string(rc))


def on_connect(unusued_client, unused_userdata, unused_flags, rc):
    print('on_connect', error_str(rc))


def on_publish(unused_client, unused_userdata, unused_mid):
    print('on_publish')


# client.on_connect = on_connect
# client.on_publish = on_publish
# 
# # Replace this with 3rd party cert if that was used when creating registry
# client.tls_set(ca_certs=root_cert_filepath)
# client.connect('mqtt.googleapis.com', 443)  
# client.loop_start()


### DECLARAMOS LOS PINES FISICOS DE CADA OBJETO
buzzer_pin = 13
temp_pin = 22
flash_pin = 12
puerta_pin = 11
trigger_pin = 3
echo_pin = 5

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
    humidity, temperature = Adafruit_DHT.read_retry(sensor_temp, temp_pin)
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
    ultrasonic = Ultrasonic(trigger=trigger_pin, echo=echo_pin)
    u_distance = ultrasonic.read_distance()
    
    if u_distance['u_distance'] <= 20:
        turn_camera_flash(True)
    else:
        turn_camera_flash(False)
    
    data_dict.update(u_distance)
    return data_dict

def turn_camera_flash(on_off):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    
    GPIO.setup(flash_pin, GPIO.OUT)
    
    if on_off:
        GPIO.output(flash_pin, GPIO.HIGH)
    else:
        GPIO.output(flash_pin, GPIO.LOW)

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
        return datosUsuario
    except requests.exceptions.ConnectionError:
        return None
    except IndexError:
        buzzer=Buzzer(13)
        buzzer.buzz(seconds=0.5)
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

puerta = Puerta( puerta_pin )

while True:
    
    adc_inputs = {
        0: 'Peso_P1',
        2: 'Peso_P2'
    }
    
    if puerta.read_door():
        print("Puerta cerrada: ", end='')
        print(get_data_dict( adc_inputs ))
        #client.username_pw_set(username='unused', password=create_jwt(registry_Fridge))

    else:
        print("Puerta abierta: ", end='')
        print(get_tag_info())
        #client.username_pw_set(username='unused', password=create_jwt(registry_Client))
        
    
    