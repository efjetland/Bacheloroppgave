import Tkinter as tk
import tkMessageBox, os, csv, time, pexpect
import matplotlib as mpl
from bluetooth import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from functools import partial
from gattlib import DiscoveryService
mpl.use('TkAgg')

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
timeOfStartString = time.strftime("%d%b,%y-%H.%M", time.gmtime())
isRunning = True
status = 0
startTime = time.time()
pauseTime = 0
timePaused = 0
devices = scan()
connectedDevices = []
activesensors = []
sensors = {}
newData = {}

#DebugInfo
timerSecond=time.time()
ticks = 0
ticksLastSecond = 0

#Test data:
timestamps = []

class Loggerapp(tk.Tk):

    def __init__(self,  *args, **kwargs):

        tk.Tk.__init__(self,  *args, **kwargs)
        tk.Tk.wm_title(self,"system")
        tk.Tk.resizable(self, width=True, height=True)
        tk.Tk.geometry(self, "800x415")
        self.maxsize(width=800, height=455)
        self.minsize(width=600, height=400)
        self.test="TestButtonThing"

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

        connectWindow.tkraise()

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
        self.optionsPanel = optionsPanel

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
        mpl.rc('lines', lw=1) #width of graph lines
        plot = figure.add_subplot(111, fc=GRAPH_COLOR) #create subplot and axes, set background on graph
        self.figure = figure
        self.plot = plot
        self.clearGraph()

        canvas = FigureCanvasTkAgg(figure, master=graphPanel) #create a canvas to draw the figure on, graphPanel is parent
        self.canvas=canvas
        canvas.show()
        canvas.get_tk_widget().pack(side="left", fill="both", expand=True, padx=14, pady=14) #add the canvas to the window

        self.l = 0

        #OPTION PANEL
        self.generateSettings(optionsPanel)

    def generateSettings(self, panel):
        self.buttons = {}
        for index, (key, value) in enumerate(sensors.items()):

            b = tk.Button(panel, text=key, bg='green', width=20, relief='flat', overrelief='flat')
            action = partial(self.toggleButton, key)
            b["command"] = action
            b.configure(state='normal', relief='flat', bg='green')
            b.grid(row=index, column=0, padx=10, pady=5)

            self.buttons[key] = [b, i]

    def toggleButton(self, name):
        print name
        print self.buttons[name][0]['bg']
        if self.buttons[name][0]['bg'] == 'green':
            self.buttons[name][0]['bg'], self.buttons[name][1]['bg'] = 'red', 'red'
            if name in activesensors:
                activesensors.remove(name)
                for i, (key, value) in enumerate(sensors.items()):
                    if key == name:
                        self.linelist[i].set_data([],[])
        else:
            self.buttons[name][0]['bg'], self.buttons[name][1]['bg'] = 'green', 'green'
            if not name in activesensors:
                activesensors.append(name)
                for i, (key, value) in enumerate(sensors.items()):
                    if key == name:
                        x = timestamps[self.l:len(timestamps)]
                        y = value[self.l:len(timestamps)]
                        self.linelist[i].set_data(x,y)

    def clearGraph(self):
        plot = self.plot
        plot.clear()
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
        self.generateSettings(self.optionsPanel)

    def startButtonAction(self):
        global status
        if status < RUNNING:
            print("Starting.")
            if status == NOTSTARTED:
                global startTime
                startTime = time.time()
                #Open file for writing
                self.csvfile = open("data/{}.csv".format(timeOfStartString), "wb")
                self.writer = csv.writer(self.csvfile)
                self.sensorOrder = []
                for name in sensors.keys():
                    self.sensorOrder.append(name)
                labels = ["Timestamps"] + self.sensorOrder
                self.writer.writerow(labels)
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
            #Close File
            self.csvfile.close()
            status = NOTSTARTED
            self.l = 0
            timestamps = []
            for key, value in sensors.items():
                sensors[key] = []
        if cont:
            self.startButtonAction()

    def updateGraph(self):
        minY = 70
        maxY = 70
        graphPadding = 3
        if timestamps[len(timestamps)-1] < 30:
            self.plot.set_xlim(0,30)
            for i, (key, value) in enumerate(sensors.items()):
                if key in activesensors:
                    x = timestamps[self.l:len(timestamps)]
                    y = value[self.l:len(timestamps)]
                    self.linelist[i].set_data(x,y)
                    if min(y) - graphPadding < minY:
                        minY = min(y) - graphPadding
                    if max(y) + graphPadding > maxY:
                        maxY = max(y) + graphPadding
                else:
                    self.linelist[i].set_data([],[])
        else:
            self.plot.set_xlim(timestamps[len(timestamps)-1]-30,timestamps[len(timestamps)-1])
            if self.l == 0:
                self.l = len(timestamps)
            for i, (key, value) in enumerate(sensors.items()):
                if key in activesensors:
                    x = timestamps[len(timestamps)-self.l:len(timestamps)]
                    y = value[len(timestamps)-self.l:len(timestamps)]
                    self.linelist[i].set_data(x,y)
                    if min(y) - graphPadding < minY:
                        minY = min(y) - graphPadding
                    if max(y) + graphPadding > maxY:
                        maxY = max(y) + graphPadding
                else:
                    self.linelist[i].set_data([],[])
        self.plot.set_ylim(minY, maxY)

        self.canvas.show()

    def saveCSVFile(self):
        with open("data/data.csv","wb") as f:
            w = csv.writer(f)
            w.writerow(["TIMES:"] + timestamps)
            for key, val in sensors.items():
                w.writerow([key] + val)
            print("Saved .csv file")

    def saveContinuouslyCSV(self):
        newData = [timestamps[len(timestamps)-1]]
        for name in self.sensorOrder:
            newData.append(sensors[name][len(sensors[name])-1])
        self.writer.writerow(newData)

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
        self.scanButton = tk.Button(buttonPanel, relief="flat", bg=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR, image=self.scanButtonImage, borderwidth=0, highlightthickness=0, padx=0, pady=0, command=self.scanForDevices)
        self.scanButton.grid(row=0, column=0, padx=10)

        self.connectButtonImage = tk.PhotoImage(file="images/connectButton.gif") #load Connect button image
        self.connectButton = tk.Button(buttonPanel, relief="flat", bg=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR, image=self.connectButtonImage, borderwidth=0, highlightthickness=0, padx=0, pady=0, command=self.connectDevice)
        self.connectButton.grid(row=0, column=1, padx=10)

        self.disconnectButtonImage = tk.PhotoImage(file="images/disconnectButton.gif") #load Scan button image
        self.disconnectButton = tk.Button(buttonPanel, relief="flat", bg=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR, image=self.disconnectButtonImage, borderwidth=0, highlightthickness=0, padx=0, pady=0, command=self.disconnectDevice)
        self.disconnectButton.grid(row=0, column=2, padx=10)

        self.continueButtonImage = tk.PhotoImage(file="images/contButton.gif") #load Scan button image
        self.continueButton = tk.Button(buttonPanel, relief="flat", bg=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR, image=self.continueButtonImage, borderwidth=0, highlightthickness=0, padx=0, pady=0, command=self.nextAction)
        self.continueButton.grid(row=0, column=3, padx=10)

    def nextAction(self):
        global sensors
        sensors = {}
        print "Moving on"
        mainWindow = self.windowController.windows["mainWindow"]

        for device in connectedDevices:
            device.start_notif()
            sensors[device.getName()] = []
            newData[device.getName()] = 0
            activesensors.append(device.getName())
        print(sensors)
        mainWindow.clearGraph()

        self.windowController.changeView("mainWindow")

    def connectDevice(self):
        selectedOption = self.deviceListBox.curselection()
        print(selectedOption)
        if selectedOption != ():
            name = self.deviceListBox.get(selectedOption)
            print name
            for key, val in devices.items():
                if val == name:
                    device = HeartRateMonitor(name, key)
                    if device.connect():
                        connectedDevices.append(device)
                        self.connectedListBox.insert(tk.END, name)
                        self.deviceListBox.delete(selectedOption)
                        break

    def scanForDevices(self):
        global devices
        devices = scan()
        print devices
        print connectedDevices
        self.deviceListBox.delete(0,tk.END)
        for address, name in devices.items():
            inList = False
            for device in connectedDevices:
                if name == device.getName():
                    inList = True
            if not inList:
                self.deviceListBox.insert(tk.END, name)

    def disconnectDevice(self):
        selectedOption = self.connectedListBox.curselection()
        print(selectedOption)
        if selectedOption != ():
            name = self.connectedListBox.get(selectedOption)
            print name
            for device in connectedDevices:
                if device.getName() == name:
                    if device.disconnect():
                        connectedDevices.remove(device)
                        self.deviceListBox.insert(tk.END, name)
                        self.connectedListBox.delete(selectedOption)
                        break

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
            for device in connectedDevices:
                data = device.fetch_data()
                print("\nSensor {}, {}".format(device.getName(), data))
                if data != -1:
                    print(data)
                    data = data.strip().split(" ")
                    newData[device.getName()] = int(data[1], 16)
                    if (int(data[0],16)&(1<<4)) != 0:
                        iterator = iter(data[2:])
                        for i, j in enumerate(iterator):
                            j = j + next(iterator)
                            k = int(j, 16)
                            #print("RR-interval-{}: {}\n".format(i, k))
                else:
                    print("Error fetching data")
                    newData[device.getName()] = 0
            #print("Loops this past second: {}".format(avgSecond))  #DEBUG
            #print("Average loops for total runtime: {}".format(avg)) #DEBUG
            if len(timestamps) == 0:
                timestamps.append(0)
            else:
                timestamps.append((time.time() - startTime - timePaused)*TIMEMULTIPLIER)
            
            for sensor, data in sensors.items():
                data.append(newData[sensor])
                print("Adding {} to {}".format(newData[sensor], sensor))
        app.updateGraph()
    app.update()

app.destroy()
