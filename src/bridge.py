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


def energy_monitor_loop():
    global switch_state

    # Process any received messages from the real radio
    energenie.loop()

    time.sleep(1)


class AutoJoinSave(Registry.Discovery):
    """A discovery agent that looks for join requests, and auto adds"""
    def __init__(self, registry, router):
        super(AutoJoinSave, self).__init__(registry, router)

    def unknown_device(self, address, message):
        ##print("unknown device auto join %s" % str(address))

        #TODO: need to make this work with correct meta methods
        ##if not OpenThings.PARAM_JOIN in message:
        try:
            j = message[OpenThings.PARAM_JOIN]
        except KeyError:
            j = None

        if j == None: # not a join
            super(AutoJoinSave, self).unknown_device(address, message)
        else: # it is a join
            # but don't forward the join request as it will be malformed with no value
            ci = self.accept_device(address, message, forward=False)
            ci.join_ack()  # Ask new class instance to send a join_ack back to physical device
            self.registry.write(self.registry.DEFAULT_FILENAME)


def discovery_autojoin():
    d = AutoJoinSave(energenie.registry, energenie.fsk_router)

if __name__ == "__main__":

    print("Starting energy monitor example")

    energenie.init()
    discovery_autojoin()

    # provide a default incoming message handler, useful for logging every message
    def incoming(address, message):
        print("\nIncoming from %s" % str(address))
    energenie.fsk_router.when_incoming(incoming)

    try:
        while True:
            energy_monitor_loop()
    finally:
        energenie.finished()

# END

