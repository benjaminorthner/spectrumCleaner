import tkinter
from pathlib import Path
import pandas as pd
import numpy as np

import matplotlib as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.widgets import RectangleSelector 


# Class for Tkinter GUI
class Gui:
    def __init__(self) -> None:

        # set properties and create main canvas
        self.root = tkinter.Tk()
        self.root.resizable(False, False)
        self.root.geometry("1280x720")
        self.root.wm_title("Spectrum Cleaner")
        self.root.configure(bg = "#FFFFFF")
        self.canvas = tkinter.Canvas(
            self.root,
            bg = "#FFFFFF",
            height = 720,
            width = 1280,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        self.canvas.place(x = 0, y = 0)

        # define path to assets
        self.ASSETS_PATH = Path(__file__).parent / Path("assets")

        # Define data path for initial plot
        self.dataFilePath = "../nanoplastic/data/2022/December/6/105PMMA_60_4x_conv.txt"

        # Create a MPLObject
        self.mplObject = MPLObject()
        
        # build the GUI
        self.buildGui()

        # connect the MPL object to the correct window/button on the GUI
        self.mplObject.linkToTkinterWindow(self.mplWindow)

        # make the initial plot
        self.mplObject.loadData(self.dataFilePath)
        self.mplObject.plotData()
        self.mplObject.updateFigure()


    # gets full path to assets
    def relative_to_assets(self, path: str) -> Path:
        return self.ASSETS_PATH / Path(path)
    
    # creates all the items on the canvas
    def buildGui(self) -> None:

        # Blue background
        self.canvas.create_rectangle(
            911.0,
            0.0,
            1280.0,
            720.0,
            fill="#A8CAD1",
            outline="")

        # Program Title
        self.canvas.create_text(
            932.0,
            26.0,
            anchor="nw",
            text="SPECTRUM CLEANER",
            fill="#FFFFFF",
            font=("Poppins ExtraBold", 32 * -1)
        )

        # Version Number
        self.canvas.create_text(
            1228.0,
            64.0,
            anchor="nw",
            text="v 0.2",
            fill="#7C9397",
            font=("Poppins ExtraBold", 14 * -1)
        )

        # File Path Text
        self.dataFilePathLabel = tkinter.Label(
            self.root,
            anchor="nw",
            text=self.dataFilePath,
            bg="#FFFFFF",
            fg="#C2C2C2",
            font=("Poppins Regular", 14 * -1)
        )
        self.dataFilePathLabel.place(
            x = 40,
            y = 683
        )
        
        # MPL Window
        self.mplWindow = tkinter.Button(
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            state="disabled"
        )
        self.mplWindow.place(
            x = 40,
            y = 37,
            width = 871 - 40,
            height= 674 - 37
        )

        # IMPORT BUTTON
        self.button_image_1 = tkinter.PhotoImage(
            file=self.relative_to_assets("button_1.png"))
        self.button_1 = tkinter.Button(
            image=self.button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command= self.importData,
            relief="flat"
        )
        self.button_1.place(
            x=1102.0,
            y=635.0,
            width=157.0,
            height=59.0
        )

        # Export Button
        self.button_image_2 = tkinter.PhotoImage(
            file=self.relative_to_assets("button_2.png"))
        button_2 = tkinter.Button(
            image=self.button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: print("button_2 clicked"),
            relief="flat"
        )
        button_2.place(
            x=932.0,
            y=635.0,
            width=157.0,
            height=59.0
        )
        
        # Clear Selection Button
        self.button_image_3 = tkinter.PhotoImage(
            file=self.relative_to_assets("button_3.png"))
        self.button_3 = tkinter.Button(
            image=self.button_image_3,
            borderwidth=0,
            highlightthickness=0,
            command=self.mplObject.clearAllSelectedPoints,
            relief="flat"
        )
        self.button_3.place(
            x=932.0,
            y=123.0,
            width=157.0,
            height=59.0
        )

        # Delte Button
        self.button_image_4 = tkinter.PhotoImage(
            file=self.relative_to_assets("button_4.png"))
        self.button_4 = tkinter.Button(
            image=self.button_image_4,
            borderwidth=0,
            highlightthickness=0,
            command=self.mplObject.deleteAllSelectedPoints,
            relief="flat"
        )
        self.button_4.place(
            x=932.0,
            y=195.0,
            width=157.0,
            height=59.0
        )


    # function connected to Import Button
    def importData(self):

        # opens file explorer a current data path location and returns chosen file path
        newFilePath = tkinter.filedialog.askopenfilename(initialdir = Path(self.dataFilePath).parent,
                                            title = "Select a File",
                                            filetypes = (("Text files",
                                                            "*.txt*"),
                                                        ("all files",
                                                            "*.*")))

        # if new selection is cancelled do nothing
        if newFilePath == ():
         return
        
        # try loading data, if it fails just return
        if self.mplObject.loadData(path=newFilePath) != 0:
            return
        
        # plot the new graph and save its path
        self.dataFilePath = newFilePath
        self.dataFilePathLabel.config(text=newFilePath)
        self.mplObject.plotData()


    # main gameLoop
    def runLoop(self) -> None:
        self.root.mainloop()

        # the following is real bad for performance:
        
        #while True:
        #    self.mplObject.updateFigure()
        #    self.root.update_idletasks()
        #    self.root.update()


# Handles everything to do with the MatPlotLib Graph
class MPLObject:

    def __init__(self) -> None:
        # init the plot
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot()
        self.fig.subplots_adjust(left=0.08, right=0.96, top=0.95, bottom=0.1)

        # initialise data and selector
        self.data = pd.DataFrame([], columns=["x", "y"])
        self.selectedPoints = pd.DataFrame([], columns=['x', 'y'])
        self.selectedScatter = self.ax.scatter([], []) # scatter plot of selected points
        self.initSelectors()


    def linkToTkinterWindow(self, mplWindow: tkinter.Button) -> None:
        # link to tkinter window
        self.pltCanvas = FigureCanvasTkAgg(self.fig, master=mplWindow)
        self.pltCanvas.draw()   
        
        # Create the MPL toolbar
        self.toolbar = NavigationToolbar2Tk(self.pltCanvas, mplWindow, pack_toolbar=False)
        self.toolbar.update()


        # Packing for Tkinter (idk how this works)
        self.toolbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        self.pltCanvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

    # callback for rectangle selector (when mouse click is released)
    def onselect(self, eclick, erelease):

        # get click coordinates 
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        
        # check which points were inside the selection
        # saved as a bool dataframe where each point is marked as TRUE if selected or FALSE if no selcted
        mask = (self.data['x'] > min(x1, x2)) & (self.data['x'] < max(x1, x2)) & (self.data['y'] > min(y1, y2)) & (self.data['y'] < max(y1, y2))

        # if left click add points to selection and plot
        if eclick.button == 1:
            self.selectedPoints = pd.concat([self.selectedPoints, self.data[mask]]).drop_duplicates()
            self.plotSelectedScatter() 
            
        # if right click remove points from selection then plot
        if eclick.button == 3:
            # Merge existing with selected points and then remove the points present in both from the existing
            merged = self.selectedPoints.merge(self.data[mask], left_index=True, right_index=True)
            self.selectedPoints = self.selectedPoints[~self.selectedPoints.index.isin(merged.index)]
            self.plotSelectedScatter() 

    # removes old scatter plot of selected points and plots the new one
    def plotSelectedScatter(self) -> None:
        self.selectedScatter.remove()
        self.selectedScatter = self.ax.scatter(self.selectedPoints['x'], self.selectedPoints['y'], marker='x', color="C3")

        self.updateFigure()

    # loads new data and returns 0 if it worked and 1 if it failed
    def loadData(self, path=None) -> int:
        if path == None:
            return 0
        
        try:
            # load in new data and remove all selected points from the dataframe
            self.data = pd.read_csv(path, names=["x", "y"], sep="\t",skiprows=22)
            self.clearAllSelectedPoints()

        except:
            print("LOADING FAILED")
            return 1
        
        return 0

    # removes all selected points from the dataframe
    def clearAllSelectedPoints(self): 
        self.selectedPoints.drop(self.selectedPoints.index, inplace=True)
        self.plotSelectedScatter()

    # deletes all selected points
    def deleteAllSelectedPoints(self):
        self.data.drop(self.selectedPoints.index, inplace=True)
        self.clearAllSelectedPoints()
        self.plotData()

    # clear axes and plot the curently loaded data
    def plotData(self) -> None:
        self.clearPlot()

        # calc margins
        spectrumXWidth = max(self.data['x']) - min(self.data['x'])
        spectrumYWidth = max(self.data['y']) - min(self.data['y'])

        self.ax.set_xlim(min(self.data['x']) - 0.05 * spectrumXWidth, max(self.data['x']) + 0.05*spectrumXWidth)
        self.ax.set_ylim(min(self.data['y']) - 0.05 * spectrumYWidth, max(self.data['y']) + 0.05*spectrumYWidth)
 
        self.ax.plot(self.data['x'], self.data['y'])

        self.updateFigure()

    # clear the axis and reinit the selector
    def clearPlot(self) -> None:
        self.ax.cla()
        self.initSelectors()

    def initSelectors(self) -> None:
        # left click
        self.rectLeft = RectangleSelector(self.ax, onselect=self.onselect, button=1, useblit=True, props=dict(facecolor='red', edgecolor='black', alpha=0.2, fill=True))
        # right click
        self.rectRight = RectangleSelector(self.ax, onselect=self.onselect, button=3, useblit=True, props=dict(facecolor='green', edgecolor='black', alpha=0.2, fill=True))

    def updateFigure(self) -> None:
        self.pltCanvas.draw()
        
# create a GUI and run the loop
gui = Gui()
gui.runLoop()