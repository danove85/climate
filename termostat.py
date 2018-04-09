import sys
import signal
import time
from pymodbus.client.sync import ModbusTcpClient
import requests
import logging
from logging.handlers import RotatingFileHandler
import atexit


COOLING_COIL = 16
HEATING_COIL = 17
ENABLED = True
DISABLED = False

# Setting the format of log output

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s', datefmt='%d/%m/%Y %H:%M:%S:')


# Logging function

def setup_logger(name, log_file, level=logging.INFO):

    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = RotatingFileHandler(log_file, maxBytes=20000, backupCount=10)
        handler.setFormatter(formatter)
        logger.setLevel(level)
        logger.addHandler(handler)

    return logger

temp_logger = setup_logger('temperature_is', 'temperature.log')
get_temp_logger = setup_logger('get_temp_except', 'exceptions.log')
input_logger = setup_logger('input_exception', 'exceptions.log')
adam_logger = setup_logger('adam_exception', 'exceptions.log')

# Used to catch SIGHUP signal if the user simply closes the terminal window

def sighup_handler(signal, frame):

    client.write_coil(16, False)
    client.write_coil(17, False)
    client.close()
    sys.exit(0)


# Used to catch KeyBoardInterrupt and turn off the relays

def relay_disengager():
    
    client.write_coil(16, False)
    client.write_coil(17, False)
    client.close()


# ADAM control function

def change_component_state(client, component_name, coil_number, enabled):
    try:
        result = client.read_coils(coil_number)
        
        if result.bits[0] != enabled:
            client.write_coil(coil_number, enabled)
            print "%s relay is %s" % (component_name, 'active' if enabled else 'not active')
    
    except:
        print "Unable to connect to ADAM"
        adam_logger.error("Unable to connect to ADAM")
        raise
    return

# Cooling controls


def cool_engage(client):
    change_component_state(client, 'Cooling', COOLING_COIL, ENABLED)
       
def cool_disengage(client):
    change_component_state(client, 'Cooling', COOLING_COIL, DISABLED)

# Heating controls

def heat_engage(client):
    change_component_state(client, 'Heating', HEATING_COIL, ENABLED)
  
def heat_disengage(client):
    change_component_state(client, 'Heating', HEATING_COIL, DISABLED)

        

###########-Main program-#############

# Taking input, making sure it is a float and setting the range of input

while True:
    try:
        set_temp = raw_input('Please enter desired temperature. Range is -10 to +30 degrees Celsius:')
        set_temp = float(set_temp)
        if set_temp > -11.0 and set_temp <31:
            break
        
        else:
            print "Out of range"
    
    except ValueError:
        print "Only numbers please."
        input_logger.warning(set_temp) 


signal.signal(signal.SIGHUP, sighup_handler)
atexit.register(relay_disengager)

# Infinite loop

client = None

while True:
    
    # Defining the ADAM module
    if client is None:
        client = ModbusTcpClient('10.0.0.1')
    
    try:
        # Getting the temperature from the sensor
        read_temp = requests.get('http://10.0.0.2/statusjsn.js?components=18179').json()['sensor_values'][0]['values'][0][0]['v']
        
        print "Current temperature is: %.01f C, Set temperature is: %.01f C" % (read_temp, set_temp)
        
        temp_logger.info('%.01f', read_temp)
        
        # If temperature is lower than requested temperature
        if read_temp <= set_temp - 2.0:
            heat_engage(client)
            cool_disengage(client)
        
        # If temperature is higher than requested temperature    
        elif read_temp >= set_temp + 2.0:
            heat_disengage(client)
            cool_engage(client)

        # If temperature is  within +- 2 degrees of requested temperature
        else:
            cool_disengage(client)
            heat_disengage(client)
            print "Stabilizing temperature"
            
    except:

        try:
            client.close()
        except:
            pass

        client = None

        print "Unable to get temperature from temp sensor"
        get_temp_logger.error("Unable to get temperature from temp sensor")

    time.sleep(10)




