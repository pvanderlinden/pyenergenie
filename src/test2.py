from __future__ import print_function
import thread
import Queue
import json
import time
import energenie.radio as radio
import energenie.OnAir as OnAir
import energenie.OpenThings as OpenThings
import sys

CRYPT_PID = 242

q = Queue.Queue()
air_interface = OnAir.OpenThingsAirInterface()

def init():
    print("radio.init", file=sys.stderr)
    radio.init()

    print("OpenThings.init", file=sys.stderr)
    OpenThings.init(CRYPT_PID)

    print("thread.start_new_thread", file=sys.stderr)
    thread.start_new_thread(read_from_stdin, ())

def loop():
    print("loop", file=sys.stderr)
    while True:
        message = listen_to_radio()
        write_message(message)
        if message:
            transmit_next_queued_message()

def might_be_etrv(payload):
    if len(payload) < 3:
        return False
    return payload[1] == 4 and payload[2] == 3

# write JSON representation of an OpenThings message to stdout
def write_message(message):
    if message:
        sys.stdout.write(json.dumps(message.pydict))
        sys.stdout.write("\n")
        sys.stdout.flush()

def listen_to_radio(receive_time=1):
    #print("listen_to_radio", file=sys.stderr)
    radio.receiver(fsk=True)
    now = time.time()
    timeout = now + receive_time

    while now < timeout:
        if radio.is_receive_waiting():
            payload = radio.receive_cbp()
#            print('RX:', payload, file=sys.stderr)
            now = time.time()

            if might_be_etrv(payload):
                # debugging: dump encoded message to stderr
                print("RX:", payload, file=sys.stderr)

                try:
                    return OpenThings.decode(payload, receive_timestamp=now)
                except OpenThings.OpenThingsException:
                    pass

        now = time.time()

    return None

def transmit_next_queued_message():
    if not q.empty():
        # take top message from the queue and transmit it
        message = q.get()
        air_interface.send(message)

        # debugging: dump encoded message to stderr
        print("TX:", OpenThings.encode(message), file=sys.stderr)

def read_from_stdin():
    while True:
        try:
            # parse JSON representation of an OpenThings message
            message = OpenThings.Message(pydict=json.loads(raw_input()))

            # add it to the queue
            q.put(message)
        except:
            # TODO: log errors to stderr
            pass

init()
loop()

# Test msg for stdin:
#{"header": {"sensorid": 2003, "productid": 3, "mfrid": 4}, "recs": [{"wr": true, "paramid": 116, "typeid": 144, "length": 2, "value": 15.0}]}
