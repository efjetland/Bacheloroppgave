from gattlib import DiscoveryService, GATTRequester
import pexpect

def scan():
    service = DiscoveryService("hci0")
    devices = service.discover(2)
    return devices

class BluetoothDevice(object):
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.spawn = pexpect.spawn("gatttool -t random -I -b {0}".format(address))

    def connect(self):
        try:
            self.spawn.sendline("connect")
            self.spawn.expect("Connection successful", timeout=10)
            return True
        except pexpect.TIMEOUT:
            return False

    def disconnect(self):
        self.spawn.sendline("disconnect")
        return True

    def read_hnd(self, hnd):
        try:
            self.spawn.sendline("char-read-hnd {}".format(hnd))
            self.spawn.expect("Characteristic value/descriptor:", timeout=5)
            self.spawn.expect("\r\n", timeout=5)
            return self.spawn.before
        except pexpect.exceptions.TIMEOUT:
            return "Error reading handle"

    def write_char(self, char, value):
        try:
            self.spawn.sendline("char-write-req {} {}".format(char, value))
            self.spawn.expect("Characteristic value was written successfully")
            return True
        except pexpect.exceptions.TIMEOUT:
            return False

    def getName(self):
        return self.name

    def getAddress(self):
        return self.address

    def setName(self, name):
        self.name = name

class HeartRateMonitor(BluetoothDevice):
    def __init__(self, name, address):
        super(HeartRateMonitor, self).__init__(name, address)
        self.isRunning = False

    def start_notif(self):
        char = "0x0011"
        val = "0100"
        if self.write_char(char, val):
            self.isRunning = True
            return True
        else:
            return False

    def stop_notif(self):
        char = "0x0011"
        val = "0000"
        if self.write_char(char, val):
            self.isRunning = False
            return True
        else:
            return False

    def fetch_data(self):
        if self.isRunning:
            try:
                self.spawn.expect("value:", timeout=2)
                self.spawn.expect("\r\n")
                return self.spawn.before
            except pexpect.exceptions.TIMEOUT:
                return -1
        else:
            return -1

    def battery_level(self):
        hnd = "0x0041"
        data = self.read_hnd(hnd)
        return str(int(data, 16)) + "%"
