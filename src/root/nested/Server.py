# --------------------------------------------------------------------------- #
# import the various server implementations
# --------------------------------------------------------------------------- #
from pymodbus.server.sync import ModbusTcpServer

from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from twisted.internet.task import LoopingCall
from twisted.internet import reactor

import threading
# --------------------------------------------------------------------------- #
# configure the service logging
# --------------------------------------------------------------------------- #
#import logging

#logging.basicConfig()
#log = logging.getLogger()
#log.setLevel(logging.DEBUG)


def run_server():
    # ----------------------------------------------------------------------- #
    # initialize your data store
    # ----------------------------------------------------------------------- #

    #   di=block, co=block, hr=block, ir=block
    #   block = ModbusSequentialDataBlock(0x00, [123]*0x20)
    #   store = ModbusSlaveContext(hr=block)

    block1 = ModbusSequentialDataBlock(0x00, [0] * 0xFF)
    block2 = ModbusSequentialDataBlock(0x00, [0] * 0xFF)
    block3 = ModbusSequentialDataBlock(0x00, [0] * 0xFF)
    block4 = ModbusSequentialDataBlock(0x00, [0] * 0xFF)
    store2 = ModbusSlaveContext(co= block3, di= block4, hr=block1, ir=block2)

    slaves = {
        0xff: store2
    }

    context = ModbusServerContext(slaves=slaves, single=False)

    #   print(block1.values)
    #   print(block2.values)

    # ----------------------------------------------------------------------- #
    # initialize the server information
    # ----------------------------------------------------------------------- #
    # If you don't set this or any fields, they are defaulted to empty strings.
    # ----------------------------------------------------------------------- #
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
    identity.ProductName = 'Pymodbus Server'
    identity.ModelName = 'Pymodbus Server'
    identity.MajorMinorRevision = '1.0'

    # ----------------------------------------------------------------------- #
    # run the server you want
    # ----------------------------------------------------------------------- #
    # Tcp:
    # server = StartTcpServer(context, identity=identity, address=('0.0.0.0', 255))

    # start server in a separate thread so that is not blocking
    # server.start_server()

    # to access the blocks for slave 1
    # store_1=server.context[1]

    # to read from the block
    # print("------")
    # print(store_1.getValues(4,0,32))


    # Type-2 Implementationt
    interval = 2
    # loop = LoopingCall(f=updatevalues, a=(context,))
    # loop.start(time, now=True)
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
    address = 0x00
    contxt = a.context[slave_id_1]
    
    holding_registers = contxt.getValues(read_hReg, address, count=12)
    print("Holding Registers:")
    print(holding_registers)
    coils = contxt.getValues(read_coil, address, count=13)
    print("Coils:")
    print(coils)
    inputs = contxt.getValues(read_dI, address, count=25)
    print("Inputs:")
    print(inputs)
    print("-------------END-------------")


if __name__ == "__main__":
    run_server()