import tkinter

class MyApp:
    def __init__(self):
 
        # set properties and create main canvas
        self.root = tkinter.Tk()
        self.root.resizable(False, False)
        self.root.geometry = ("1280x720")


app = MyApp()
app.root.mainloop()