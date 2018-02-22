from gattlib import DiscoveryService, GATTRequester
import pexpect
import time

class Child:
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.spawn = pexpect.spawn("gatttool -t random -I -b {0}".format(address))
        self.isRunning = False

    def getName(self):
        return self.name

    def getAddress(self):
        return self.address

    def setName(self, name):
        self.name = name

    def connect(self):
        self.spawn.sendline("connect")
        self.spawn.expect("Connection successful", timeout=10)
        return True

    def disconnect(self):
        self.spawn.sendline("disconnect")
        self.spawn.sendline("quit")
        return True
    def start(self):
        self.spawn.sendline("char-write-req 0x0011 0100")
        self.spawn.expect("Characteristic value was written successfully")
        self.isRunning = True
        return True

    def stop(self):
        self.spawn.sendline("char-write-req 0x0011 0000")
        self.spawn.expect("Characteristic value was written successfully")
        self.isRunning = False
        return True

    def fetch_data(self):
        if self.isRunning:
            self.spawn.expect("value:", timeout=2)
            self.spawn.expect("\r\n")
            return self.spawn.before
        else:
            return -1

    def battery_level(self):
        self.spawn.sendline("char-read-hnd 0x0041")
        self.spawn.expect("Characteristic value/descriptor:")
        self.spawn.expect("\r\n")
        data = self.spawn.before
        return str(int(data, 16)) + "%"


service = DiscoveryService("hci0")
devices = service.discover(2)
device_list = []

for address, name in devices.items():
    print("name: {}, address: {}".format(name, address))
    if "Polar" in name:
        print("This is polar device: {}".format(address))
        device_list.append(address)

children = []
for ind, address in enumerate(device_list):
    child = Child(str(ind), address)
    child.connect()
    print("Battery level: " + child.battery_level())
    child.start()
    children.append(child)

    '''
    print("Running gatttool")
    child = pexpect.spawn("gatttool -t random -I -b {0}".format(address))
    print("Connecting to: {}".format(address))
    child.sendline("connect")
    child.expect("Connection successful", timeout=10)
    print("Connected successfully")
    child.sendline("char-read-hnd 0x0041")
    chind.expect("Characteristic value/descriptor:")
    child.expect("\r\n")
    print("Battery level: {}%".format(int(child.before,16)))
    child.sendline("char-write-req 0x0011 0100")
    child.expect("Characteristic value was written successfully")
    children.append(child)
    '''

log = open("log.txt", "w+")
log.write("\n\n---- Starting logging at: " + time.ctime(time.time()) + " ---- \n\n")
while True:
    for ind, child in enumerate(children):
        data = child.fetch_data()
        print("\n\nSensor {}:\n".format(child.getName()))
        log.write("\n\nSensor {}:\n".format(child.getName()))
        if data != -1:
            print(data)
            log.write("Raw data: " + data + "\n")
            data = data.strip().split(" ")
            print("BPM: {}".format(int(data[1], 16)))
            log.write("BPM: {} \n".format(int(data[1], 16)))
            if (int(data[0],16)&(1<<4)) != 0:
                iterator = iter(data[2:])
                for i, j in enumerate(iterator):
                    j = j + next(iterator)
                    k = int(j, 16)
                    print("RR-interval-{}: {}\n".format(i, k))
                    log.write("RR-interval-{}: {}\n".format(i, k))
        else:
            print("Error fetching data")


        '''
        child.expect("\n")
        print("\n\nSensor {}: \n".format(ind))
        log.write("\n\nSensor {}: \n".format(ind))
        if "value:" in child.before:
            print("Raw data: " + child.before.split("value:")[1])
            log.write("Raw data: " + child.before.split("value:")[1])
            data = child.before.split("value:")[1].strip().split(" ")
            print("BPM: {}".format(int(data[1],16)))
            log.write("BPM: {} \n".format(int(data[1],16)))
            if (int(data[0],16)&(1<<4)) != 0:
                iterator = iter(data[2:])
                for i, j in enumerate(iterator):
                    j = j + next(iterator)
                    k = int(j, 16)
                    print("RR-Interval-{}: {}\n".format(i, k))
                    log.write("RR-Interval-{}: {}\n".format(i, k))
        '''
