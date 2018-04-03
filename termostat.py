import time
from pymodbus.client.sync import ModbusTcpClient
import requests


    

#Cooling controls

def cool_engage(client):
    try:
        client.write_coil(16, True)
        result = client.read_coils(16)
        if result.bits[0] == True:
            print "Cooling relay is active"
        client.close()
    except:
        print " Unable to connect to ADAM"    
    return
        

def cool_disengage(client):
    try:
        client.write_coil(16, False)
        result = client.read_coils(16)
        if result.bits[0] == False:
            print "Cooling relay is not active"
        client.close()
    except:
        print " Unable to connect to ADAM"    
    return
        



#Heating controls

def heat_engage(client):
    try:
        client.write_coil(17, True)
        result = client.read_coils(17)
        if result.bits[0] == True:
            print "Heating relay is active"
        client.close()
    except:
        print " Unable to connect to ADAM"    
    return
        




def heat_disengage(client):
    try:
        client.write_coil(17, False)
        result = client.read_coils(17)
        if result.bits[0] == False:
            print "Heating relay is not active"
        client.close()
    except:
        print " Unable to connect to ADAM"    
    return
        

#Main program

z = 1
# Taking input and making sure it is a float
while z == True:
    set_temp = raw_input('Please enter desired temperature:')
    try:
        set_temp = float(set_temp)
        z = 0
    except ValueError:
        print "Temperature normally consist of numbers, not letters.....Try again please: "


#Infinite loop

while True:
    # Defining the ADAM module
    client = ModbusTcpClient('10.0.0.1')
    

    #Getting the temperature from the sensor
    try:
        read_temp = requests.get('http://10.0.0.2/statusjsn.js?components=18179').json()['sensor_values'][0]['values'][0][0]['v']
        print "Current temperature is %f " % (read_temp)
        if read_temp <= set_temp - 2.0:
            heat_engage(client)
            cool_disengage(client)
            
        elif read_temp >= set_temp + 2.0:
            heat_disengage(client)
            cool_engage(client)

        else:
            print "Stabilizing temperature"
            
    except:
        print "Unable to get temperature from temp sensor"

    
    time.sleep(5)


