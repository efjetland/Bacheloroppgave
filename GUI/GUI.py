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

#GlobalVar
isRunning = True
hasStarted = False
startTime = time.time()

#Test data:
timestamps = []
sensors = {"Sensor1":[],
           "Sensor2":[],
           "Sensor3":[]}



class Loggerapp(tk.Tk):

    frame = None
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

        self.startButtonImage = tk.PhotoImage(file="gButton.gif") #load green button image
        self.stopButtonImage = tk.PhotoImage(file="rButton.gif") #load red button image
        #create start button with image
        tk.Button(buttonPanel, relief="flat", bg=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR, image=self.startButtonImage, borderwidth=0, highlightthickness=0, padx=0, pady=0, command=self.startButtonAction).grid(row=0, column=0, sticky="N", padx=10, pady=10)
        #create stop button with image
        tk.Button(buttonPanel, relief="flat", bg=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR, image=self.stopButtonImage, borderwidth=0, highlightthickness=0, padx=0, pady=0, command=self.stopButtonAction).grid(row=0, column=1, sticky="S", padx=10, pady=10)

        figure = Figure(figsize=(5,2.4),dpi=100) #create a new figure
        figure.patch.set_facecolor(GRAPH_COLOR) #set background color around the graph
        mpl.rc('lines', lw=0.5) #width of graph lines
        plot = figure.add_subplot(111, fc=GRAPH_COLOR) #create subplot and axes, set background on graph
        self.figure = figure
        self.plot = plot
        plot.set_xlim(0, 30)
        #Plot data from each sensor
        for key, value in sensors.items():
            x = timestamps
            y = value
            self.plot.plot(x,y, label=key) #Plot the data
        plot.set_xlabel("Time")
        plot.set_ylabel("HR")
        plot.set_title("Heartratevariablility over time")
        plot.legend(loc="upper right")

        canvas = FigureCanvasTkAgg(figure, master=graphPanel) #create a canvas to draw the figure on, graphPanel is parent
        self.canvas=canvas
        canvas.show()
        canvas.get_tk_widget().pack(side="bottom", fill="both", expand=True, padx=30, pady=20) #add the canvas to the window

    def startButtonAction(self):
        global hasStarted
        if not hasStarted:
            hasStarted=True
            print("Starting.")
            global startTime
            startTime = time.time()


    def stopButtonAction(self):
        if tkMessageBox.askyesno("Confirm", "Do you really want to stop?"):

            print("Stopped at {}".format(timestamps[len(timestamps)-1]))
            global isRunning
            isRunning = False
            #Check if data directory exitsts, create if not
            directory="data/"
            if not os.path.exists(directory):
                os.makedirs(directory)
                os.chown(directory, 1000, 1000) #Change owner of the data/ folder
            #File saving options:
            self.saveDataTxt()
            self.saveRawData()
            self.saveDataJsonByTimestamps()


    def updateGraph(self):
        self.plot.clear()
        self.plot.set_ylabel("HR")
        self.plot.set_title("Heartratevariablility over time")
        self.plot.margins(tight=True)
        for key, value in sensors.items():
            x = timestamps
            y = value
            self.plot.plot(x,y, label=key) #Plot the data
        self.plot.legend(loc="upper right")
        if timestamps[len(timestamps)-1] < 30:
            self.plot.set_xlim(0,30)
        else:
            self.plot.set_xlim(timestamps[len(timestamps)-1]-30,timestamps[len(timestamps)-1])
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
#app.mainloop()
while isRunning:
    time.sleep(1)
    if hasStarted:
        if len(timestamps) == 0:
            timestamps.append(0)
        else:
            timestamps.append(time.time() - startTime)
        for ind, (key, value) in enumerate(sensors.items()):
            temp = random.randrange(5,50,1)
            sensors[key].append(temp)
        app.updateGraph()

    app.update()
    app.update_idletasks()
app.destroy()
