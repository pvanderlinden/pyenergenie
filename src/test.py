import energenie
from energenie import radio
import random
import time
from energenie import OpenThings
from energenie.Devices import fsk_interface
energenie.init()
energenie.discovery_none()
asd=None
i=0
def ack(address, message):
    global asd
    msg={
    "header": {
        "mfrid":       energenie.Devices.MFRID_ENERGENIE,
        "productid":   message['header']['productid'],
        "encryptPIP":  message['header']['encryptPIP'],
        "sensorid":    message['header']['sensorid']
    },
    "recs": [{
"wr":      False,
"paramid": OpenThings.PARAM_JOIN,
            "typeid":  OpenThings.Value.UINT,
            "length":  0, # FILL IN
    }]
}
    fsk_interface.send(msg)
    radio.receiver(fsk=True)
    asd = msg['header'].copy()

def do():
    global i
    print('start', time.time())
    types=[0x92, OpenThings.Value.UINT, OpenThings.Value.UINT_BP16, OpenThings.Value.SINT_BP16]
    PARAMS = list(OpenThings.param_info.keys())
    INFO = {'header': asd.copy()}
    INFO['header']['encryptPIP'] = int(random.random() * 65025)
    PARAM = PARAMS[i%len(PARAMS)]
    #print(OpenThings.param_info[PARAM])
    INFO["recs"] = [{
"wr":      False,
"paramid": 0x74,
            "typeid":  types[i%len(types)],
            "length":  0, # FILL IN
 #           "value": 0,
    }]
    print('sending', time.time())
    fsk_interface.send(INFO)
    print('send', time.time())
    radio.receiver(fsk=True)
    print('la', time.time())
    i+=1

def incoming(address, message):
    print('in', time.time())
    if address == (4, 2, 6711):
        return
    print("\nIncoming from {}: {}".format(address, message))
    for i in message['recs']:
        if i['paramname'] == 'JOIN':
            print('join request')
            ack(address, message)
    do()
energenie.fsk_router.when_incoming(incoming)

#device = energenie.registry.get('auto_0x3_0x4da')
#device = energenie.registry.get('auto_0x2_0x1a37')
#for i in range(0, 256):
#    INFO = {
#    "header": {
#        "mfrid":       energenie.Devices.MFRID_ENERGENIE,
#        "productid":   device.product_id,
#        "encryptPIP":  energenie.Devices.CRYPT_PIP,
#        "sensorid":    device.device_id
#    },
#    "recs": [{
#"wr":      False,
#"paramid": i,
#            "typeid":  OpenThings.Value.UINT,
#            "length":  0, # FILL IN
# "value": 0,
#    }]
#}
#    device.send_message(INFO)
#    print(i)
#    energenie.loop(1)
while True:
    energenie.loop(5)
energenie.finished()
