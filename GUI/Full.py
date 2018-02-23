import Tkinter as tk
import tkMessageBox, os, csv
import matplotlib as mpl
import time
mpl.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from gattlib import DiscoveryService
import pexpect

#Constants
LARGE_FONT = ("Verdana", 35)
MEDIUM_FONT = ("Verdana", 15)
SMALL_FONT = ("Verdana", 10)
BACKGROUND_COLOR = "#393939"
GRAPH_COLOR = "#B8B8B8"
TIMEMULTIPLIER = 1 #Debug variable to "speed up" time

#STATUS CONSTANTS
NOTSTARTED = 0
PAUSED = 1
RUNNING = 2

#GlobalVar
isRunning = True
status = 0
startTime = time.time()
pauseTime = 0
timePaused = 0
service = DiscoveryService("hci0")
devices = service.discover(2)
connectedDevices = []
deviceList = []

#DebugInfo
timerSecond=time.time()
ticks = 0
ticksLastSecond = 0

#Test data:
timestamps = []
sensors = {"Sensor1":[],
           "Sensor2":[],
           "Sensor3":[]}
discoveredBluetoothDevices= {"PolarBelt1":"1293128973981273",
                             "PolarBelt12":"1212312312311273",
                             "PolarBelt13":"1231231981271231",
                             "PolarBelt14":"1267978967897273",
                             "PolarBelt42":"1212312312311273",
                             "PolarBelt23":"1231231981271231",
                             "PolarBelt34":"1267978967897273",
                             "PolarBelt32":"1212312312311273",
                             "PolarBelt43":"1231231981271231",
                             "PolarBelt44":"1267978967897273",
                             "PolarBelt52":"1212312312311273",
                             "PolarBelt53":"1231231981271231",
                             "PolarBelt54":"1267978967897273",
                             "PolarBelt62":"1212312312311273",
                             "PolarBelt73":"1231231981271231",
                             "PolarBelt84":"1267978967897273",
                             "PolarBelt5":"1293121849418465"}

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
            try:
                self.spawn.expect("value:", timeout=2)
                self.spawn.expect("\r\n")
                return self.spawn.before
            except pexpect.exceptions.TIMEOUT:
                return -1
        else:
            return -1

    def battery_level(self):
        self.spawn.sendline("char-read-hnd 0x0041")
        self.spawn.expect("Characteristic value/descriptor:")
        self.spawn.expect("\r\n")
        data = self.spawn.before
        return str(int(data, 16)) + "%"


class Loggerapp(tk.Tk):

    def __init__(self,  *args, **kwargs):

        tk.Tk.__init__(self,  *args, **kwargs)
        tk.Tk.wm_title(self,"system")
        tk.Tk.resizable(self, width=True, height=True)
        tk.Tk.geometry(self, "800x415")
        self.maxsize(width=800, height=455)
        self.minsize(width=600, height=400)
        self.test="TestButtonTHing"

        container = tk.Frame(self) #Container frame, full window
        container["bg"] = BACKGROUND_COLOR #Set the background color of the main window
        container.pack(side="bottom", fill="both", expand=True) #Pack the full frame

        self.windows = {}

        startWindow = StartWindow(container, self) #Store the content of the start window class in a variable, set it's parent to the container view
        startWindow.grid(row=0, column=0, sticky="nsew")
        startWindow["bg"] = BACKGROUND_COLOR #set the background color of the startWindow class
        self.windows["startWindow"] = startWindow

        mainWindow = MainWindow(container, self) #Store the content of the main window class in a variable, set it's parent to the container view
        mainWindow.grid(row=0, column=0, sticky="nsew")
        mainWindow["bg"] = BACKGROUND_COLOR #set the background color of the MainWindow class
        self.windows["mainWindow"] = mainWindow

        connectWindow = ConnectionWindow(container, self) #Store the content of the main window class in a variable, set it's parent to the container view
        connectWindow.grid(row=0, column=0, sticky="nsew")
        connectWindow["bg"] = BACKGROUND_COLOR #set the background color of the MainWindow class
        self.windows["connectWindow"] = connectWindow

        mainWindow.tkraise()

    def updateGraph(self):
        self.windows["mainWindow"].updateGraph()


    def changeView(self, windowName):
        self.windows[windowName].tkraise()

class StartWindow(tk.Frame):

    def __init__(self, parent, windowController):
        tk.Frame.__init__(self, parent)
        tk.Button(self, text=windowController.test, command=self.nextAction).grid(pady=200,padx=400)
        self.windowController = windowController

    def nextAction(self):
        self.windowController.changeView("mainWindow")

class MainWindow(tk.Frame):


    def __init__(self, parent, controller):

        self.windowController = controller
        tk.Frame.__init__(self, parent) #initialize the main window frame

        buttonPanel = tk.Frame(self, bg=BACKGROUND_COLOR, pady=15) #container for buttons
        buttonPanel.grid(column=0, row=1, sticky="S") #add the container to the mainwindow frame on the second row
        graphPanel = tk.Frame(self, bg=BACKGROUND_COLOR) #container for the graph
        graphPanel.grid(column=0,row=0) #add the container to the mainwindow frame on the first row
        optionsPanel = tk.Frame(self, bg="#303030", width=186, height=415)
        optionsPanel.grid(column=1, row=0, rowspan=2, sticky="NE")

        #BUTTON SECTION
        self.startButtonImage = tk.PhotoImage(file="images/gButton.gif") #load green button image
        self.stopButtonImage = tk.PhotoImage(file="images/rButton.gif") #load red button image
        self.pauseButtonImage = tk.PhotoImage(file="images/yButton.gif") #laod yellow button image
        #create start button with image
        self.startButton = tk.Button(buttonPanel, relief="flat", bg=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR, image=self.startButtonImage, borderwidth=0, highlightthickness=0, padx=0, pady=0, command=self.startButtonAction)
        self.startButton.grid(row=0, column=0, sticky="N", padx=50, pady=10)
        #create stop button with image
        self.stopButton = tk.Button(buttonPanel, relief="flat", bg=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR, image=self.stopButtonImage, borderwidth=0, highlightthickness=0, padx=0, pady=0, command=self.stopButtonAction)
        self.stopButton.grid(row=0, column=1, sticky="S", padx=50, pady=10)
        #create pause button with image, but don't add it to UI yet
        self.pauseButton = tk.Button(buttonPanel, relief="flat", bg=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR, image=self.pauseButtonImage, borderwidth=0, highlightthickness=0, padx=0, pady=0, command=self.pauseButtonAction)

        #GRAPH SECTION
        figure = Figure(figsize=(5.86,2.3),dpi=100) #create a new figure
        figure.patch.set_facecolor(GRAPH_COLOR) #set background color around the graph
        mpl.rc('lines', lw=0.5) #width of graph lines
        plot = figure.add_subplot(111, fc=GRAPH_COLOR) #create subplot and axes, set background on graph
        self.figure = figure
        self.plot = plot
        plot.set_xlim(0, 30)
        plot.set_ylim(0, 70)
        plot.margins(tight=True)
        self.linelist = []
        #Plot data from each sensor
        for key, value in sensors.items():
            x = timestamps
            y = value
            line, = plot.plot(x,y, label=key)
            print(line)
            self.linelist.append(line) #Plot the data
        plot.set_xlabel("Time")
        plot.set_ylabel("HR")
        plot.set_title("Heartratevariablility over time")
        plot.legend(loc="upper right")


        canvas = FigureCanvasTkAgg(figure, master=graphPanel) #create a canvas to draw the figure on, graphPanel is parent
        self.canvas=canvas
        canvas.show()
        canvas.get_tk_widget().pack(side="left", fill="both", expand=True, padx=14, pady=14) #add the canvas to the window

        self.l = 0

    def startButtonAction(self):
        global status
        if status < RUNNING:
            print("Starting.")
            if status == NOTSTARTED:
                global startTime
                startTime = time.time()
            if status == PAUSED:
                global timePaused, pauseTime
                timePaused += (time.time() - pauseTime)
            status = RUNNING
            self.pauseButton.grid(row=0, column=0, sticky="N", padx=10, pady=10)
            self.startButton.grid_remove()

    def pauseButtonAction(self):
        global status
        if status == RUNNING:
            global pauseTime
            pauseTime = time.time()
            print("Pausing.")
            self.startButton.grid(row=0, column=0, sticky="N", padx=10, pady=10)
            self.pauseButton.grid_remove()
            status = PAUSED

    def stopButtonAction(self):
        global status, timestamps
        cont = False
        if status == RUNNING:
            self.pauseButtonAction()
            cont = True
        if status != NOTSTARTED and tkMessageBox.askyesno("Confirm", "Do you really want to stop?"):
            print("Stopped at {}".format(timestamps[len(timestamps)-1]))
            cont = False
            if status == RUNNING:
                self.startButton.grid(row=0, column=0, sticky="N", padx=10, pady=10)
                self.pauseButton.grid_remove()
            #Check if data directory exitsts, create if not
            directory="data/"
            if not os.path.exists(directory):
                os.makedirs(directory)
                os.chown(directory, 1000, 1000) #Change owner of the data/ folder
            #File saving options:
            #self.saveDataTxt()
            #self.saveRawData()
            #self.saveDataJsonByTimestamps()
            self.saveCSVFile()
            status = NOTSTARTED
            self.l = 0
            timestamps = []
            for key, value in sensors.items():
                sensors[key] = []
        if cont:
            self.startButtonAction()

    def updateGraph(self):
        if timestamps[len(timestamps)-1] < 30:
            self.plot.set_xlim(0,30)
            for i, (key, value) in enumerate(sensors.items()):
                x = timestamps[self.l:len(timestamps)]
                y = value[self.l:len(timestamps)]
                self.linelist[i].set_data(x,y)
        else:
            self.plot.set_xlim(timestamps[len(timestamps)-1]-30,timestamps[len(timestamps)-1])
            if self.l == 0:
                self.l = len(timestamps)
            for i, (key, value) in enumerate(sensors.items()):
                x = timestamps[len(timestamps)-self.l:len(timestamps)]
                y = value[len(timestamps)-self.l:len(timestamps)]
                self.linelist[i].set_data(x,y)




        self.canvas.show()

    def saveDataTxt(self):
        with open("data/data.txt", "w") as f:
            f.write("Timestamps: ")
            for time in timestamps:
                if time%1==0:
                    f.write("    {}.0".format(time))
                else:
                    f.write("    {}".format(time))
            f.write("\n")
            for sensor in sensors.keys():
                f.write("Data from sensor {}:".format(sensor))
                for data in sensors[sensor]:
                    if data<10:
                        f.write("    0{}".format(data))
                    else:
                        f.write("    {}".format(data))

                f.write("\n")
            f.write("Stopped at {}".format(timestamps[len(timestamps)-1]))
            print("Saved .txt file")

    def saveDataJsonByTimestamps(self):
        with open("data/data.json", "w") as f:
            f.write('{\n"Timestamps":\n    {\n')
            for time in timestamps:
                if time != timestamps[0]:
                    f.write(",\n")
                f.write('        "{}":\n'.format(time))
                f.write("            {")
                for index, (key, value) in enumerate(sensors.items()):
                    if index>0:
                        f.write(",")
                    f.write('"{}":{}'.format(key,value[timestamps.index(time)]))
                f.write('}')
            f.write("\n    }\n}")
            print("Saved .json file")

    def saveRawData(self):
        with open("data/data.dat", "w") as f:
            f.write("{}\n".format(timestamps))
            f.write("{}".format(sensors))
            print("Saved .dat file")

    def saveCSVFile(self):
        with open("data/data.csv","wb") as f:
            w = csv.writer(f)
            w.writerow(["TIMES:"] + timestamps)
            for key, val in sensors.items():
                w.writerow([key] + val)
            print("Saved .csv file")

class ConnectionWindow(tk.Frame):

    def __init__(self, parent, windowController):
        self.windowController = windowController
        tk.Frame.__init__(self, parent)

        #Main layout of connection screen
        leftPanel = tk.Frame(self, bg=BACKGROUND_COLOR, padx=30)
        leftPanel.grid(row=0, column=0, sticky="NEWS", padx=0)
        rightPanel = tk.Frame(self, bg=BACKGROUND_COLOR, padx=30)
        rightPanel.grid(row=0, column=1, sticky="NEWS", padx=0)
        buttonPanel = tk.Frame(self, bg=BACKGROUND_COLOR, pady=22, padx=15)
        buttonPanel.grid(row=1, column=0, columnspan=2, sticky="SEW")

        #LeftPanel setup
        deviceListLabel = tk.Label(leftPanel,text="Nearby Devices", font=MEDIUM_FONT, bg=BACKGROUND_COLOR, fg="#b3b3b3")
        deviceListLabel.grid(row=0,column=0, sticky="N", padx=5)
        scrollbar = tk.Scrollbar(leftPanel, orient=tk.VERTICAL)
        deviceListBox = tk.Listbox(leftPanel, width=40, height=14, bg=GRAPH_COLOR, bd=0, font=SMALL_FONT, highlightthickness=0, relief="flat", activestyle="dotbox", yscrollcommand=scrollbar.set)
        deviceListBox.grid(row=1,column=0, sticky="E")
        scrollbar.config(command=deviceListBox.yview)
        scrollbar.grid(row=1, column=1, sticky="WNS")
        for device in devices.keys():
            deviceListBox.insert(tk.END, devices[device])
        self.deviceListBox = deviceListBox


        #RightPanel setup
        connectedListLabel = tk.Label(rightPanel,text="Connected Devices", font=MEDIUM_FONT, bg=BACKGROUND_COLOR, fg="#b3b3b3")
        connectedListLabel.grid(row=0, column=0, sticky="N", padx=5)
        scrollbar = tk.Scrollbar(rightPanel, orient=tk.VERTICAL)
        connectedListBox = tk.Listbox(rightPanel, width=40, height=14, bg=GRAPH_COLOR, bd=0, font=SMALL_FONT, highlightthickness=0, relief="flat", activestyle="dotbox", yscrollcommand=scrollbar.set)
        connectedListBox.grid(row=1,column=0, sticky="E")
        scrollbar.config(command=connectedListBox.yview)
        scrollbar.grid(row=1, column=1, sticky="WNS")
        self.connectedListBox = connectedListBox

        #ButtonPanel setup
        self.scanButtonImage = tk.PhotoImage(file="images/scanButton.gif") #load Scan button image
        self.scanButton = tk.Button(buttonPanel, relief="flat", bg=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR, image=self.scanButtonImage, borderwidth=0, highlightthickness=0, padx=0, pady=0)
        self.scanButton.grid(row=0, column=0, padx=10)

        self.connectButtonImage = tk.PhotoImage(file="images/connectButton.gif") #load Connect button image
        self.connectButton = tk.Button(buttonPanel, relief="flat", bg=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR, image=self.connectButtonImage, borderwidth=0, highlightthickness=0, padx=0, pady=0, command=self.connectDevice)
        self.connectButton.grid(row=0, column=1, padx=10)

        self.disconnectButtonImage = tk.PhotoImage(file="images/disconnectButton.gif") #load Scan button image
        self.disconnectButton = tk.Button(buttonPanel, relief="flat", bg=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR, image=self.disconnectButtonImage, borderwidth=0, highlightthickness=0, padx=0, pady=0)
        self.disconnectButton.grid(row=0, column=2, padx=10)

        self.continueButtonImage = tk.PhotoImage(file="images/contButton.gif") #load Scan button image
        self.continueButton = tk.Button(buttonPanel, relief="flat", bg=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR, image=self.continueButtonImage, borderwidth=0, highlightthickness=0, padx=0, pady=0)
        self.continueButton.grid(row=0, column=3, padx=10)

    def nextAction(self):
        self.windowController.changeView("mainWindow")

    def connectDevice(self):
        selectedOption = self.deviceListBox.curselection()
        if selectedOption != "":
            name = self.deviceListBox.get(selectedOption)
            print name
            connectedDevices.append(name)
            self.connectedListBox.insert(tk.END, name)
            self.deviceListBox.delete(selectedOption)
            for key, val in devices.items():
                if val == name:
                    child = Child(name, key)
                    print "connection status for {}: {}".format(name, child.connect())
                    children.append(child)

    def scanForDevices(self):
        global devices
        devices = service.discover(2)
        print devices
        print deviceList
        print connectedDevices
        for address, name in devices.items():
            if address not in connectedDevices:
                connectedDevices.append(address)


children = []
sensors = {}
app = Loggerapp()
#Main Loop
while isRunning:
    
    if status == RUNNING:
        ticks+=1
        ticksLastSecond+=1
        avg = ticks / (time.time() - startTime- timePaused)
        if time.time() - timerSecond >= 1: #Code that will only run if more that a second has passed since last time the block started
            avgSecond = ticksLastSecond/(time.time()-timerSecond)
            ticksLastSecond = 0
            timerSecond=time.time()
            #print("Loops this past second: {}".format(avgSecond))  #DEBUG
            #print("Average loops for total runtime: {}".format(avg)) #DEBUG
            
            for child in children:
                data = child.fetch_data()
                print("\n\nSensor {}:\n".format(child.getName()))
                if data != -1:
                    print(data)
                    data = data.strip().split(" ")
                    sensors[child.getName()].append(int(data[1], 16))
                    if (int(data[0],16)&(1<<4)) != 0:
                        iterator = iter(data[2:])
                        for i, j in enumerate(iterator):
                            j = j + next(iterator)
                            k = int(j, 16)
                            print("RR-interval-{}: {}\n".format(i, k))
                else:
                    print("Error fetching data")
                    sensors[child.getName()].append(0)
            if len(timestamps) == 0:
                timestamps.append(0)
            else:
                timestamps.append((time.time() - startTime - timePaused)*TIMEMULTIPLIER)
        app.updateGraph()

    app.update()


app.destroy()
