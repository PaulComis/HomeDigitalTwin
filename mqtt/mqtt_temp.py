#!python3

# Raspbery pi - Python MQTT sender

# Import python libraries
import paho.mqtt.client as mqtt
import json
import time
import os

#print($HOME)

# Globals
# Need a better way of grabbing these
THINGSBOARD_HOST = '192.168.0.42'
TOKEN = 'ESykq9oQrEyg3l4uRBzw'
# Function to get the core CPU temperature
def getTemp():
    try:
        # CPU Temperature is written to this file...
        tempFile = open('/sys/class/thermal/thermal_zone0/temp')
    except Exception as err:
        print('Unknown shit happened')
        print(err)
        return None
    else:
        temp = float(tempFile.read())
        tempCelcius = temp/1000
        return tempCelcius

# Callback function - CONNACK request from an MQTT server
def on_connect(client, userdata, rc, *extra_params):
    print('connecting')
    #Subscribe for RPC requests
    # Question - what is this literal?...
    try:
        client.subscribe ('v1/devices/me/rpc/request/+')
    #sensor_data['CPU Temperature'] = getTemp()
    #publish = json.dumps(sensor_data)
    # As above
    #try:
    #    client.publish('v1/devices/me/telemetry', publish, 1)
    except Exception as err:
        print('bad things happened')
        print(err)
    
def getClientToken():
    home = os.environ['HOME']
    keyFileName = home + '/.ssh/thingsboard_token'
    try:
        keyFile = open(keyFileName)
        print('reading', keyFileName)
    except Exception as err:
        print('Could not get authorisation token')
        print(err)
        exit
    else:
        token = keyFile.readline()
        return token
    
# Programme initialisation
sensor_data = {'CPU Temperature': 0}
try:
    client = mqtt.Client()
except Exception as err:
    print('Could not initialise MQTT client')
    print(err)
    exit

client.on_connect = on_connect

token = getClientToken()
tokenAsString = str(token)

print(TOKEN)
print(tokenAsString)

try:
    client.username_pw_set(tokenAsString)
#    client.username_pw_set(TOKEN)
except Exception as err:
    print('Nope token')
    print(err)

try:
    client.connect(THINGSBOARD_HOST, 1883, 60)
except Exception as err:
    print('Nope', err)
    exit
        
client.loop_start()
    
#Main Loop
try:
    while True:
        sensor_data['CPU Temperature'] = getTemp()
        publish = json.dumps(sensor_data)
        try:
            client.publish('v1/devices/me/telemetry', publish, 1)
            print (publish)
        except Exception as err:
                print('MQTT Publish failure')
                print(err)
        time.sleep(2)
except KeyboardInterrupt:
    print ('Ctrl-C Pressed')
    client.loop_stop(force=False)
except Exception as err:
    print('Some other error')
    print(err)
finally:
    print('Done')
    exit