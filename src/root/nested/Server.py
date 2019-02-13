
from pymodbus.server.sync import ModbusTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
import socket
import threading


def run_arduino_server():

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = ('127.0.0.1', 9050)
    print("Server is on this IP: {}".format(server_address))
    sock.bind(server_address)

    while True:
        data, address = sock.recvfrom(4096)
    
        print("Received")
        print(data)
    
        if data:
            sent = sock.sendto(data, address)
            print("Sent")
            print(data)


def run_server():

    block1 = ModbusSequentialDataBlock(0x00, [0] * 0xFF)
    block2 = ModbusSequentialDataBlock(0x10, [0] * 0xFF)
    block3 = ModbusSequentialDataBlock(0x00, [0] * 0xFF)
    block4 = ModbusSequentialDataBlock(0x00, [0] * 0xFF)
    store1 = ModbusSlaveContext(co= block3, di=block4, hr=block1, ir= block2)
    store2 = ModbusSlaveContext(co= block3, di= block4, hr=block1, ir=block2)

    slaves = {
        0xFF: store1
    }

    context = ModbusServerContext(slaves=slaves, single=False)

    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
    identity.ProductName = 'Pymodbus Server'
    identity.ModelName = 'Pymodbus Server'
    identity.MajorMinorRevision = '1.0'

    interval = 1
    server = ModbusTcpServer(context, identity=identity,
                            address=('0.0.0.0', 502))
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    loop = LoopingCall(f=updatevalues, a=server)
    loop.start(interval, now=True)
    reactor.run()
    
    

def updatevalues(a):
    
    print("------------START----------")
    read_coil = 1
    read_dI = 2
    read_hReg = 3
    read_iReg = 4
    write_sCoil= 5
    write_sReg = 6
    write_mCoils = 15
    write_mReg = 16 
    
    slave_id_1 = 0xff
    slave_id_2 = 0xff
    
    address = 0x00
    CA = a.context[slave_id_1]
    
    holding_registers = CA.getValues(read_hReg, address, count=25)
    print("Holding Registers:")
    print(holding_registers)
    coils = CA.getValues(read_coil, address, count=12)
    print("Coils:")
    print(coils)
    inputs = CA.getValues(read_dI, address, count=10)
    print("Inputs:")
    print(inputs)
    print("-------------END-------------")
    
    contxt = a.context[slave_id_1]
    contxt.setValues(read_dI, 0x00, [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0])
    contxt.setValues(write_mReg, 0x00, [0, 0, 0, 0, 0 ,0 , 26, 26, 26, 26, 26, 26])
    
    

if __name__ == "__main__":
    run_server()
