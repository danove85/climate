from pymodbus.client.sync import ModbusTcpClient

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


client = ModbusTcpClient('10.0.0.1')

cool_disengage(client)
heat_disengage(client) 