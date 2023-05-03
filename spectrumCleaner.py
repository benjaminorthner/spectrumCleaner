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
        self.mplObject.updateFigure()


    # gets full path to assets
    def relative_to_assets(self, path: str) -> Path:
        return self.ASSETS_PATH / Path(path)
    
    # loads the current path in again (callback function of reset button)
    def reset(self) -> None:
        self.mplObject.loadData(path=self.dataFilePath)

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
            text="v 0.3",
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
        self.button_image_7 = tkinter.PhotoImage(
            file=self.relative_to_assets("button_7.png"))
        self.button_7 = tkinter.Button(
            image=self.button_image_7,
            borderwidth=0,
            highlightthickness=0,
            command=self.mplObject.clearAllSelectedPoints,
            relief="flat"
        )
        self.button_7.place(
            x=983.0,
            y=180.0,
            width=48.88970947265625,
            height=47.286773681640625
        )

        self.canvas.create_text(
            1047.11767578125,
            190.4191131591797,
            anchor="nw",
            text="Clear Selection",
            fill="#FFFFFF",
            font=("Poppins Regular", 20 * -1)
        )

        # Delete Button
        self.button_image_6 = tkinter.PhotoImage(
            file=self.relative_to_assets("button_6.png"))
        self.button_6 = tkinter.Button(
            image=self.button_image_6,
            borderwidth=0,
            highlightthickness=0,
            command=self.mplObject.deleteAllSelectedPoints,
            relief="flat"
        )
        self.button_6.place(
            x=983.0,
            y=236.10293579101562,
            width=48.88970947265625,
            height=47.286766052246094
        )

        self.canvas.create_text(
            1047.0,
            247.0,
            anchor="nw",
            text="Delete Selection",
            fill="#FFFFFF",
            font=("Poppins Regular", 20 * -1)
        )

        # Reset button
        self.button_image_5 = tkinter.PhotoImage(
            file=self.relative_to_assets("button_5.png"))
        self.button_5 = tkinter.Button(
            image=self.button_image_5,
            borderwidth=0,
            highlightthickness=0,
            command=self.reset,
            relief="flat"
        )
        self.button_5.place(
            x=983.0,
            y=292.0,
            width=48.88970947265625,
            height=47.286766052246094
        )

        self.canvas.create_text(
            1047.0,
            302.8970642089844,
            anchor="nw",
            text="Reset",
            fill="#FFFFFF",
            font=("Poppins Regular", 20 * -1)
        )

        # Show Points Button
        self.button_image_4 = tkinter.PhotoImage(
            file=self.relative_to_assets("button_4.png"))
        self.button_4 = tkinter.Button(
            image=self.button_image_4,
            borderwidth=0,
            highlightthickness=0,
            command=self.mplObject.toggleDataScatter,
            relief="flat"
        )
        self.button_4.place(
            x=983.0,
            y=390.0,
            width=48.88970947265625,
            height=47.286766052246094
        )

        self.canvas.create_text(
            1047.0,
            400.8970642089844,
            anchor="nw",
            text="Show Points",
            fill="#FFFFFF",
            font=("Poppins Regular", 20 * -1)
        )

        # Show line button
        self.button_image_3 = tkinter.PhotoImage(
            file=self.relative_to_assets("button_3.png"))
        self.button_3 = tkinter.Button(
            image=self.button_image_3,
            borderwidth=0,
            highlightthickness=0,
            command=self.mplObject.toggleDataLine,
            relief="flat"
        )
        self.button_3.place(
            x=983.0,
            y=446.0,
            width=48.88970947265625,
            height=47.286773681640625
        )

        self.canvas.create_text(
            1047.0,
            456.8970642089844,
            anchor="nw",
            text="Show Line",
            fill="#FFFFFF",
            font=("Poppins Regular", 20 * -1)
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
        self.fig = Figure(figsize=(5, 4), dpi=120)
        self.ax = self.fig.add_subplot()
        self.fig.subplots_adjust(left=0.08, right=0.96, top=0.95, bottom=0.1)

        # initialise data and selectors
        self.data = pd.DataFrame([], columns=["x", "y"])
        self.dataLine,  = self.ax.plot([], [])
        self.hiddenDataLine,  = self.ax.plot([], [])
        self.dataScatter = self.ax.scatter([], [])
        self.showingDataLine = True
        self.showingDataScatter = False # keeps track if data scatter is visible

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

    # loads new data and returns 0 if it worked and 1 if it failed
    def loadData(self, path=None) -> int:
       
        try:
            # load in new data and remove all selected points from the dataframe
            self.data = pd.read_csv(path, names=["x", "y"], sep="\t",skiprows=22)

        except:
            print("LOADING FAILED")
            return 1
        
        # If loading was successful then also plot
        self.clearAllSelectedPoints()
        self.ax.cla()
        self.initSelectors()
        
        # calc margins
        spectrumXWidth = max(self.data['x']) - min(self.data['x'])
        spectrumYWidth = max(self.data['y']) - min(self.data['y'])

        self.ax.set_xlim(min(self.data['x']) - 0.05 * spectrumXWidth, max(self.data['x']) + 0.05*spectrumXWidth)
        self.ax.set_ylim(min(self.data['y']) - 0.05 * spectrumYWidth, max(self.data['y']) + 0.05*spectrumYWidth)

        # Plot the data 
        self.plotDataLine()

        # If scatter is enabled, show it
        if self.showingDataScatter: self.plotDataScatter()


        # necessary so zoom doesnt change after point deletion
        self.plotDataLine(hidden=True) 
        
        self.updateFigure()
        return 0

    def toggleDataLine(self) -> None:
        if self.showingDataLine:
            self.dataLine.set_alpha(0)
        else:
            self.dataLine.set_alpha(1)
        
        self.showingDataLine = not self.showingDataLine
        self.updateFigure()

    def plotDataLine(self, hidden=False):
        # plots the hidden line needed to mentain zoom level
        if hidden:
            self.hiddenDataLine, = self.ax.plot(self.data['x'], self.data['y'], color='red', alpha=0.1, zorder=-1)
            return
        
        # clear the current line before plotting the new one
        self.dataLine.remove()

        alpha = 1 if self.showingDataLine else 0
        self.dataLine,  = self.ax.plot(self.data['x'], self.data['y'], color='gray', alpha=alpha, zorder=0)

        self.updateFigure()


    # toggle the scatter plot for all data points (button callback function)
    def toggleDataScatter(self) -> None:
        if self.showingDataScatter:
            self.dataScatter.remove()
        else:
            self.plotDataScatter()

        # toggle the state and update
        self.showingDataScatter = not self.showingDataScatter
        self.updateFigure()

    # plot the scatterplot of the raw data
    def plotDataScatter(self) -> None:
            self.dataScatter = self.ax.scatter(self.data['x'], self.data['y'], s=8, marker='x', color="k", zorder=1)

    # removes old scatter plot of selected points and plots the new one
    def plotSelectedScatter(self) -> None:
        self.selectedScatter.remove()
        self.selectedScatter = self.ax.scatter(self.selectedPoints['x'], self.selectedPoints['y'], s=10, marker='x', color="C3", zorder=2)
        self.updateFigure()

    # removes all selected points from the dataframe
    def clearAllSelectedPoints(self): 
        self.selectedPoints.drop(self.selectedPoints.index, inplace=True)
        self.plotSelectedScatter()

    # deletes all selected points
    def deleteAllSelectedPoints(self):
        self.data.drop(self.selectedPoints.index, inplace=True)
        self.clearAllSelectedPoints()
        self.plotDataLine()
        if self.showingDataScatter:
            self.toggleDataScatter()
            self.toggleDataScatter()

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