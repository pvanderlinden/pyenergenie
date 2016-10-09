from __future__ import print_function
from energenie import OpenThings
from energenie import Devices
import datetime

IDENTIFY_REQ = {
    "header": {
        "mfrid":       Devices.MFRID,
        "productid":   Devices.PRODUCTID_MIHO013,
        "encryptPIP":  Devices.CRYPT_PIP,
        "sensorid":    1242
    },
    "recs": [
        {
            "wr":      True,
            "paramid": 0x3F,
            "typeid":  OpenThings.Value.UINT,
            "length":  0
        }
    ]
}

EXERCISE_COMMAND = {
    "header": {
        "mfrid":       Devices.MFRID,
        "productid":   Devices.PRODUCTID_MIHO013,
        "encryptPIP":  Devices.CRYPT_PIP,
        "sensorid":    1242
    },
    "recs": [
        {
            "wr":      True,
            "paramid": 0x23,
            "typeid":  OpenThings.Value.UINT,
            "length":  0
        }
    ]
}

SET_REPORTING_INTERVAL = {
    "header": {
        "mfrid":       Devices.MFRID,
        "productid":   Devices.PRODUCTID_MIHO013,
        "encryptPIP":  Devices.CRYPT_PIP,
        "sensorid":    1242
    },
    "recs": [
        {
            "wr":      True,
            "paramid": 0x52,
            "typeid":  OpenThings.Value.UINT,
            "value":  240,
        }
    ]
}


GET_BATTERY_VOLTAGE = {
    "header": {
        "mfrid":       Devices.MFRID,
        "productid":   Devices.PRODUCTID_MIHO013,
        "encryptPIP":  Devices.CRYPT_PIP,
        "sensorid":    1242
    },
    "recs": [
        {
            "wr":      True,
            "paramid": 0x62,
            "typeid":  OpenThings.Value.UINT,
            "length": 0,
        }
    ]
}

SET_VALVE_STATE = {
    "header": {
        "mfrid":       Devices.MFRID,
        "productid":   Devices.PRODUCTID_MIHO013,
        "encryptPIP":  Devices.CRYPT_PIP,
        "sensorid":    1242
    },
    "recs": [
        {
            "wr":      True,
            "paramid": 0x25,
            "typeid":  OpenThings.Value.UINT,
            "value": 0,
            "length": 1,
        }
    ]
}

GET_DIAGNOSTICS = {
    "header": {
        "mfrid":       Devices.MFRID,
        "productid":   Devices.PRODUCTID_MIHO013,
        "encryptPIP":  Devices.CRYPT_PIP,
        "sensorid":    1242
    },
    "recs": [
        {
            "wr":      True,
            "paramid": 0x26,
            "typeid":  OpenThings.Value.UINT,
            "length": 0,
        }
    ]
}

SET_TARGET_TEMPERATURE = {
    "header": {
        "mfrid":       Devices.MFRID,
        "productid":   Devices.PRODUCTID_MIHO013,
        "encryptPIP":  Devices.CRYPT_PIP,
        "sensorid":    1242
    },
    "recs": [
        {
            "wr":      True,
            "paramid": 0x74,
            "typeid":  0x90,
            "value": 21.0,
        }
    ]
}

SET_ROOM_TEMP = {
    "header": {
        "mfrid":       Devices.MFRID,
        "productid":   Devices.PRODUCTID_MIHO013,
        "encryptPIP":  Devices.CRYPT_PIP,
        "sensorid":    1242
    },
    "recs": [
        {
            "wr":      False,
            "paramid": 0x74,
            "typeid":  0x90,
            "value": 16.0,
        }
    ]
}
# TODO: how?
CLEAR_ROOM_TEMP = {
    "header": {
        "mfrid":       Devices.MFRID,
        "productid":   Devices.PRODUCTID_MIHO013,
        "encryptPIP":  Devices.CRYPT_PIP,
        "sensorid":    1242
    },
    "recs": [
        {
            "wr":      False,
            "paramid": 0x74,
            "typeid":  OpenThings.Value.UINT,
            "length": 0,
        }
    ]
}

SET_LOW_POWER_LEVEL = {
    "header": {
        "mfrid":       Devices.MFRID,
        "productid":   Devices.PRODUCTID_MIHO013,
        "encryptPIP":  Devices.CRYPT_PIP,
        "sensorid":    1242
    },
    "recs": [
        {
            "wr":      True,
            "paramid": 0x24,
            "typeid":  OpenThings.Value.UINT,
            "value": 0,
            "length": 1,
        }
    ]
}


# Test program with easy device:

SWITCH_MESSAGE = {
    "header": {
        "mfrid":       Devices.MFRID,
        "productid":   Devices.PRODUCTID_MIHO005,
        "encryptPIP":  Devices.CRYPT_PIP,
        "sensorid":    6711,
    },
    "recs": [
        {
            "wr":      True,
            "paramid": OpenThings.PARAM_SWITCH_STATE,
            "typeid":  OpenThings.Value.UINT,
            "length":  1,
            "value":   0,
        }
    ]
}

JOIN_ACK = {
    "header": {
        "mfrid":       Devices.MFRID,
        "productid":   Devices.PRODUCTID_MIHO013,
        "encryptPIP":  Devices.CRYPT_PIP,
        "sensorid":    1242,
    },
    "recs": [
        {
            "wr":      False,
            "paramid": OpenThings.PARAM_JOIN,
            "typeid":  OpenThings.Value.UINT,
            "length":  0,
        }
    ]
}

#####

def combine(*msgs):
    combined = {'header': msgs[0]['header'], 'recs': []}
    for msg in msgs:
        assert msg['header'] == combined['header']
        combined['recs'].extend(msg['recs'])
    return combined


to_send = [
    CLEAR_ROOM_TEMP,#GET_BATTERY_VOLTAGE,# SET_TARGET_TEMPERATURE,#SET_ROOM_TEMP,#SET_VALVE_STATE,#SET_TARGET_TEMPERATURE,#SET_VALVE_STATE,#IDENTIFY_REQ,
    #SWITCH_MESSAGE,
]

def dct_to_address(dct):
    return (dct['header']['mfrid'], dct['header']['productid'], dct['header']['sensorid'])
#
# HRF_send_FSK_msg(HRF_make_FSK_msg(manufacturerId, encryptId, productId, sensorId,
#                                   4, 0xD2, 0x02, 0x03, 0x84), encryptId);

import zmq
import json
import time

context = zmq.Context()
sub = context.socket(zmq.SUB)
sub.connect('tcp://127.0.0.1:12347')
sub.setsockopt(zmq.SUBSCRIBE, b'')
push = context.socket(zmq.PUSH)
push.connect('tcp://127.0.0.1:12348')

from collections import defaultdict
class cycledict(dict):

    def __getitem__(self, name):
        if not hasattr(self, '_cycles'):
            self._cycles = defaultdict(lambda: 0)
        item =  dict.__getitem__(self, name)
        result = item[self._cycles[name]%len(item)]
        self._cycles[name]+=1
        return result 
by_address = {dct_to_address(msg): msg for msg in to_send}
for address in by_address.keys():
    msg = by_address[address]
    push.send('address {}'.format(json.dumps(address)).encode('utf-8'))
    push.send('msg %s' % json.dumps(msg).encode('utf-8'))
while True:
    msg = sub.recv().decode('utf-8')
    msg_type, msg = msg.split(' ', 1)
    msg = json.loads(msg)
    if msg_type == 'switch_data':
        address = dct_to_address(msg)
        if address in by_address:
            push.send('msg %s' % json.dumps(by_address[address]).encode('utf-8'))
            print(datetime.datetime.now(), msg)
    elif msg_type == 'switch_next':
        address = tuple(msg[0])
        if address not in by_address:
            continue
        next = msg[1]
        if next:
            next = datetime.datetime.fromtimestamp(next)
        print(address, next)
