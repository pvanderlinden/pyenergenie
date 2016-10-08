# mihome_energy_monitor.py  28/05/2016  D.J.Whale
#
# A simple demo of monitoring and logging energy usage of mihome devices
#
# Logs all messages to screen and to a file energenie.csv
# Any device that has a switch, it toggles it every 2 seconds.
# Any device that offers a power reading, it displays it.

import energenie
from energenie import Registry
from energenie import OpenThings

import time
import json

import zmq

last_message = {}
last_freq = {}

def get_next(address):
    last_msg = last_message.get(address, None)
    last_frq = last_freq.get(address, None)
    if last_msg and last_frq:
        return last_msg + last_frq
    return None

schedule = {}
def dct_to_address(dct):
    return (dct['header']['mfrid'], dct['header']['productid'], dct['header']['sensorid'])

def energy_monitor_loop(pull, pub):
    global switch_state

    # Process any received messages from the real radio
    energenie.loop()

    if pull.poll(timeout=1):
        msg = pull.recv().decode('utf-8')
        try:
            msg_type, msg = msg.split(' ', 1)
        except:
            print('error', msg)
        msg = json.loads(msg)
        if msg_type == 'msg':
            device = energenie.registry.get('auto_0x{:x}_0x{:x}'.format(msg['header']['productid'], msg['header']['sensorid']))
            schedule[dct_to_address(msg)] = (device, OpenThings.encode(msg))
        elif msg_type == 'address':
            address = tuple(msg)
            next = get_next(address)
            pub.send('switch_next {}'.format(json.dumps((address, next))).encode('utf-8'))

class AutoJoinSave(Registry.Discovery):
    """A discovery agent that looks for join requests, and auto adds"""
    def __init__(self, registry, router):
        Registry.Discovery.__init__(self, registry, router)

    def unknown_device(self, address, message):
        ##print("unknown device auto join %s" % str(address))

        #TODO: need to make this work with correct meta methods
        ##if not OpenThings.PARAM_JOIN in message:
        try:
            j = message[OpenThings.PARAM_JOIN]
        except KeyError:
            j = None

        if j == None: # not a join
            Registry.Discovery.unknown_device(self, address, message)
        else: # it is a join
            # but don't forward the join request as it will be malformed with no value
            ci = self.accept_device(address, message, forward=False)
            ci.join_ack()  # Ask new class instance to send a join_ack back to physical device
            self.registry.store.write(self.registry.DEFAULT_FILENAME)


def discovery_autojoin():
    d = AutoJoinSave(energenie.registry, energenie.fsk_router)

if __name__ == "__main__":

    print("Starting energy monitor example")

    energenie.init()
    discovery_autojoin()
    class Dummy:
        pass
    energenie.registry.load_into(Dummy())

    context = zmq.Context()
    pub = context.socket(zmq.PUB)
    pub.bind('tcp://127.0.0.1:12347')
    pull = context.socket(zmq.PULL)
    pull.bind('tcp://127.0.0.1:12348')

    def incoming(address, message):
        now = time.time()
        out_msg = schedule.pop(address, None)
        if out_msg:
            out_msg[0].send_message(out_msg[1], encoded=True)
        pub.send('{} {}'.format(
                 'switch_data', json.dumps(message.pydict)).encode('utf-8'))
        last = last_message.get(address, None)
        if last:
            freq = 'previous: %ss ago' % (now - last)
            last_freq[address] = now - last
        else:
            freq = 'first message'
        last_message[address] = now
        print("\n%s Incoming from %s, %s: %s" % (time.time(), str(address), freq, message))
        next = get_next(address)
        pub.send('switch_next {}'.format(json.dumps((address, next))).encode('utf-8'))
    energenie.fsk_router.when_incoming(incoming)

    try:
        while True:
            energy_monitor_loop(pull, pub)
    finally:
        energenie.finished()

# END

