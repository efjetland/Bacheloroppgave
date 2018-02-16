from gattlib import DiscoveryService, GATTRequester, GATTResponse
from time import sleep
import pygatt
from binascii import hexlify

class Requester(GATTRequester):
    def on_notification(self, handle, data):
        print("- notification on handle: {}\n".format(handle))

def handle_data(handle, value):
    print("received data: %s" % hexlify(value))

adapter = pygatt.GATTToolBackend()

service = DiscoveryService("hci0")
devices = service.discover(2)

for address, name in devices.items():
    print("name: {}, address: {}".format(name, address))
    if "Polar" in name:
        print("Connecting to polar device: {}".format(address))
        #req = GATTRequester(address, False)
        #req.connect()
        #name = req.read_by_uuid("0x0011")
        #print(name)
        try:
            adapter.start()
            device = adapter.connect(address)
            device.subscribe("0x2a37", callback=handle_data)
        finally:
            adapter.stop()
        
while True:
    print("Doing a sleep")
    sleep(1)
