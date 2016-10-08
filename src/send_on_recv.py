
# message = {}
#
# HRF_send_FSK_msg(HRF_make_FSK_msg(manufacturerId, encryptId, productId, sensorId,
#                                   4, 0xD2, 0x02, 0x03, 0x84), encryptId);

import zmq
import json

context = zmq.Context()
sub = context.socket(zmq.SUB)
sub.connect('tcp://127.0.0.1:12347')
sub.setsockopt(zmq.SUBSCRIBE, b'')
push = context.socket(zmq.PUSH)
push.connect('tcp://127.0.0.1:12348')

while True:
    msg = sub.recv().decode('utf-8')
    msg_type, msg = msg.split(' ', 1)
    msg = json.loads(msg)
    print(msg)
