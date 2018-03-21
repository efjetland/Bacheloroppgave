timestamps = []
activesensors = []
sensors = {}

def updateGraph(self):
        minY = 70
        maxY = 70
        graphPadding = 3
        graphXSeconds = 50
        dataLength = 0
        latestTime = timestamps[len(timestamps)-1]
        if latestTime < graphXSeconds:
            self.plot.set_xlim(0,graphXSeconds)
            dataLength = len(timestamps)
        else:
            self.plot.set_xlim(latestTime-graphXSeconds,latestTime)
            dataLength = graphXSeconds

        for i, (key, value) in enumerate(sensors.items()):
            if key in activesensors:
                if latestTime < graphXSeconds:
                    x = timestamps
                    y = value
                else:
                    x = timestamps[len(timestamps)-dataLength:len(timestamps)]
                    y = value[len(value)-dataLength:len(value)]
                self.linelist[i].set_data(x,y)
                if min(y) - graphPadding < minY:
                    minY = min(y) - graphPadding
                if max(y) + graphPadding > maxY:
                    maxY = max(y) + graphPadding
            else:
                self.linelist[i].set_data([],[])

        self.plot.set_ylim(minY, maxY)

        self.canvas.show()
