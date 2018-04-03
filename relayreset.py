from pymodbus.client.sync import ModbusTcpClient

def cool_disengage(client):
    client.write_coil(16, False)
    result = client.read_coils(16)
    print "Cooling relay state is " + str(result.bits[0])
    client.close()
    return

def heat_disengage(client):

    client.write_coil(17, False)
    result = client.read_coils(17)
    print "Heat relay state is " +  str(result.bits[0])
    client.close()
    return 


client = ModbusTcpClient('10.0.0.1')

cool_disengage(client)
heat_disengage(client) 