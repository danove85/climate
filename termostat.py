import sys
import signal
import time
from pymodbus.client.sync import ModbusTcpClient
import requests
import logging
from logging.handlers import RotatingFileHandler
import atexit


#Setting the format of log output

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s', datefmt='%d/%m/%Y %H:%M:%S:')


#Logging function

def setup_logger(name, log_file, level=logging.INFO):

    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = RotatingFileHandler(log_file, maxBytes=10000, backupCount=10)
        handler.setFormatter(formatter)
        logger.setLevel(level)
        logger.addHandler(handler)

    return logger

#Used to catch SIGHUP signal if the user simply closes the terminal window

def sighup_handler(signal, frame):

    client.write_coil(16, False)
    client.write_coil(17, False)
    client.close()
    sys.exit(0)


#Used to catch KeyBoardInterrupt and turn off the relays

def relay_disengager():
    
    client.write_coil(16, False)
    client.write_coil(17, False)
    client.close()


#Cooling controls

def cool_engage(client):
    try:
        result = client.read_coils(16)
        
        if result.bits[0] != True:
            client.write_coil(16, True)
            print "Cooling relay is active"
        
        client.close()
    
    except:
        print "Unable to connect to ADAM"
        adam_logger = setup_logger('adam_exception', 'exceptions.log')
        adam_logger.error("Unable to connect to ADAM")    
    return
        

def cool_disengage(client):
    try:
        result = client.read_coils(16)
        if result.bits[0] != False:
            client.write_coil(16, False)
            print "Cooling relay is not active"
        
        client.close()
    
    except:
        print "Unable to connect to ADAM"
        adam_logger = setup_logger('adam_exception', 'exceptions.log')
        adam_logger.error("Unable to connect to ADAM")    
    return
        



#Heating controls

def heat_engage(client):
    try:
        result = client.read_coils(17)
        if result.bits[0] != True:
            client.write_coil(17, True)
            print "Heating relay is active"
        
        client.close()
    
    except:
        print "Unable to connect to ADAM"
        adam_logger = setup_logger('adam_exception', 'exceptions.log')
        adam_logger.error("Unable to connect to ADAM")    
    return
        




def heat_disengage(client):
    try:
        result = client.read_coils(17)
        if result.bits[0] != False:
            client.write_coil(17, False)
            print "Heating relay is not active"
        
        client.close()
    
    except:
        print "Unable to connect to ADAM"
        adam_logger = setup_logger('adam_exception', 'exceptions.log')
        adam_logger.error("Unable to connect to ADAM")    
    return
        

###########-Main program-#############

# Taking input, making sure it is a float and setting the range of input

z = 1

while z == True:
    try:
        set_temp = raw_input('Please enter desired temperature. Range is -10 to +30 degrees Celsius:')
        set_temp = float(set_temp)
        if set_temp > -11.0 and set_temp <31:
            z = 0
        
        else:
            print "Out of range"
    
    except ValueError:
        print "Only numbers please."
        input_logger = setup_logger('input_exception', 'exceptions.log')
        input_logger.warning(set_temp) 


#Infinite loop

while True:
    
    # Defining the ADAM module
    client = ModbusTcpClient('10.0.0.1')
    
    try:
        #Getting the temperature from the sensor
        read_temp = requests.get('http://10.0.0.2/statusjsn.js?components=18179').json()['sensor_values'][0]['values'][0][0]['v']
        
        print "Current temperature is: %f C, Set temperature is: %f C" % (read_temp, set_temp)
        temp_logger = setup_logger('temperature_is', 'temperature.log')
        temp_logger.info(read_temp)
        
        #If temperature is lower than requested temperature
        if read_temp <= set_temp - 2.0:
            heat_engage(client)
            cool_disengage(client)
        
        #If temperature is higher than requested temperature    
        elif read_temp >= set_temp + 2.0:
            heat_disengage(client)
            cool_engage(client)

        #If temperature is  within +- 2 degrees of requested temperature
        else:
            cool_disengage(client)
            heat_disengage(client)
            print "Stabilizing temperature"
            
    except:
        print "Unable to get temperature from temp sensor"
        get_temp_logger = setup_logger('get_temp_except', 'exceptions.log')
        get_temp_logger.error("Unable to get temperature from temp sensor")

    signal.signal(signal.SIGHUP, sighup_handler)
    atexit.register(relay_disengager)
    time.sleep(5)




