import wx
class Launcher(wx.Frame):
    def __init__(self,parent=None):
        self.main_view =wx.Frame.__init__(self, parent, title = 'Tree Launcher')
        self.initialize()
    def initialize(self):
        self.panel = wx.Panel(self, wx.ID_ANY, size=wx.Size(800,800))
        self.sizer_title = wx.BoxSizer(wx.VERTICAL)
        self.main_title = wx.StaticText(self.panel, wx.ID_ANY, label = "Arboles")
        #self.sizer_title.Add(self.main_title,0, wx.ALL|wx.EXPAND, 5)
        self.Show()