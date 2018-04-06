from pymodbus.client.sync import ModbusTcpClient

def read_cool_relay(client):
    try:
        result = client.read_coils(16, 1)
        if result.bits[0] == False:
            print "Cooling relay is not active"
        elif result.bits[0] == True:
            print "Cooling relay is active"
        client.close()
    except:
        print " Unable to connect to ADAM"    
    return

def read_heat_relay(client):
    try:
        result = client.read_coils(17)
        if result.bits[0] == False:
            print "Heating relay is not active"
        elif result.bits[0] == True:
            print "Heating relay is active"
        client.close()
    except:
        print " Unable to connect to ADAM"
    return 


client = ModbusTcpClient('10.0.0.1')

read_cool_relay(client)
read_heat_relay(client) 