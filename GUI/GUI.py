import Tkinter as tk
import tkMessageBox, os
import matplotlib as mpl
import time
mpl.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import random

#Constants
LARGE_FONT = ("Verdana", 35)
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

#DebugInfo
timerSecond=time.time()
ticks = 0
ticksLastSecond = 0

#Test data:
timestamps = []
sensors = {"Sensor1":[],
           "Sensor2":[],
           "Sensor3":[]}

class Loggerapp(tk.Tk):

    def __init__(self,  *args, **kwargs):

        tk.Tk.__init__(self,  *args, **kwargs)
        tk.Tk.wm_title(self,"system")
        tk.Tk.resizable(self, width=True, height=True)
        tk.Tk.geometry(self, "800x415")
        self.maxsize(width=800, height=455)
        self.minsize(width=600, height=400)

        container = tk.Frame(self) #Container frame, full window
        container["bg"] = BACKGROUND_COLOR #Set the background color of the main window
        container.pack(side="bottom", fill="both", expand=True) #Pack the full frame

        frame = MainWindow(container) #Store the content of the main window class in a variable, set it's parent to the container view
        frame.pack(anchor="w")
        frame["bg"] = BACKGROUND_COLOR #set the background color of the MainWindow class
        frame.tkraise() #Display the window
        self.frame = frame

    def updateGraph(self):
        self.frame.updateGraph()

class MainWindow(tk.Frame):
    figure=None
    plot=None
    canvas = None

    def __init__(self, parent):
        tk.Frame.__init__(self, parent) #initialize the main window frame

        buttonPanel = tk.Frame(self, bg=BACKGROUND_COLOR, pady=15) #container for buttons
        buttonPanel.grid(column=0, row=1, sticky="S") #add the container to the mainwindow frame on the second row
        graphPanel = tk.Frame(self, bg=BACKGROUND_COLOR) #container for the graph
        graphPanel.grid(column=0,row=0) #add the container to the mainwindow frame on the first row
        optionsPanel = tk.Frame(self, bg="#303030", width=186, height=415)
        optionsPanel.grid(column=1, row=0, rowspan=2, sticky="NE")

        #BUTTON SECTION
        self.startButtonImage = tk.PhotoImage(file="gButton.gif") #load green button image
        self.stopButtonImage = tk.PhotoImage(file="rButton.gif") #load red button image
        self.pauseButtonImage = tk.PhotoImage(file="yButton.gif") #laod yellow button image
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
            self.saveDataTxt()
            self.saveRawData()
            self.saveDataJsonByTimestamps()
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

    def saveRawData(self):
        with open("data/data.dat", "w") as f:
            f.write("{}\n".format(timestamps))
            f.write("{}".format(sensors))

app = Loggerapp()

#Main Loop
while isRunning:

    if status == RUNNING:
        if len(timestamps) == 0:
            timestamps.append(0)
        else:
            timestamps.append((time.time() - startTime - timePaused)*TIMEMULTIPLIER)
        for ind, (key, value) in enumerate(sensors.items()):
            temp = random.randrange(5,50,1)
            sensors[key].append(temp)
        app.updateGraph()

        ticks+=1
        ticksLastSecond+=1
        avg = ticks / (time.time() - startTime- timePaused)
        if time.time() - timerSecond > 1:
            avgSecond = ticksLastSecond/(time.time()-timerSecond)
            ticksLastSecond = 0
            timerSecond=time.time()
            print("Loops this past second: {}".format(avgSecond))
            print("Average loops for total runtime: {}".format(avg))
    app.update()


app.destroy()
