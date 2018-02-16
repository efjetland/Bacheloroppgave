from gattlib import DiscoveryService, GATTRequester
import pexpect
import time

service = DiscoveryService("hci0")
devices = service.discover(2)
device_list = []

for address, name in devices.items():
    print("name: {}, address: {}".format(name, address))
    if "Polar" in name:
        print("This is polar device: {}".format(address))
        device_list.append(address)

children = []
for address in device_list:
    print("Running gatttool")
    child = pexpect.spawn("gatttool -t random -I -b {0}".format(address))
    print("Connecting to: {}".format(address))
    child.sendline("connect")
    child.expect("Connection successful", timeout=10)
    print("Connected successfully")
    child.sendline("char-write-req 0x0011 0100")
    child.expect("Characteristic value was written successfully")
    f = open("log.txt", "w+")
    children.append(child)
    
while True:
    for ind, child in enumerate(children):
        child.expect("\n")
        print("\n\nSensor {}: \n".format(ind))
        if "value:" in child.before:
            print(child.before.split("value:")[0])
            data = child.before.split("value:")[1].strip().split(" ")
            for i, j in enumerate(data):
                k = int(j,16)
                print("{}: {} = {}".format(i, j, k))
            
        print("Length: " + str(len(child.before)))
        f.write(child.before)
