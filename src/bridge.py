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


def energy_monitor_loop(pull):
    global switch_state

    # Process any received messages from the real radio
    energenie.loop()

    if pull.poll(timeout=1):
        msg = json.loads(pull.recv().decode('utf-8'))

        device = energenie.registry.get('auto_0x{:x}_0x{:x}'.format(msg['header']['productid'], msg['header']['sensorid']))
        device.send_message(msg)


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

    # provide a default incoming message handler, useful for logging every message
    last_message = {}
    def incoming(address, message):
        pub.send('{} {}'.format(
                 'switch_data', json.dumps(message.pydict)).encode('utf-8'))
        now = time.time()
        last = last_message.get(address, None)
        if last:
            freq = 'previous: %ss ago' % (now - last)
        else:
            freq = 'first message'
        last_message[address] = now
        print("\nIncoming from %s, %s: %s" % (str(address), freq, message))
    energenie.fsk_router.when_incoming(incoming)

    try:
        while True:
            energy_monitor_loop(pull)
    finally:
        energenie.finished()

# END

