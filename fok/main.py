import dotenv
import os

import wx
from wx.lib.agw.piectrl import ProgressPie
from wx.lib.floatcanvas.FCObjects import PieChart

dotenv.load_dotenv()

class ControlFrame(wx.Frame):
    def __init__(self):
        super(ControlFrame, self).__init__(None, title= "Bender "+os.environ.get("VERSION"), size=(640, 480))

        self.InitUI()
        self.Centre()
    def InitUI(self):
        self.BackgroundColour = "white"
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour("red")
        self.panel.closeButton = wx.Button(self.panel, label = "OK")
        self.panel.chart = ProgressPie(self.panel, 100, 10, pos=(10, 50), size=(100, 100))



def main():

    app = wx.App()
    control_frame = ControlFrame()
    control_frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()