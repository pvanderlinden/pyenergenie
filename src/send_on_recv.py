from __future__ import print_function
from energenie import OpenThings
from energenie import Devices
import datetime

# IDENTIFY_REQ = {
#     "header": {
#         "mfrid":       Devices.MFRID,
#         "productid":   Devices.PRODUCTID_MIHO013,
#         "encryptPIP":  Devices.CRYPT_PIP,
#         "sensorid":    1242
#     },
#     "recs": [
#         {
#             "wr":      True,
#             "paramid": 0x3F,
#             "typeid":  OpenThings.Value.UINT,
#             "length":  0
#         }
#     ]
# }

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
            "value":  0 
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
    combine(SET_REPORTING_INTERVAL, GET_BATTERY_VOLTAGE),
#    SWITCH_MESSAGE,
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

by_address = {dct_to_address(msg): msg for msg in to_send}
for address in by_address:
    push.send('address {}'.format(json.dumps(address)).encode('utf-8'))
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
