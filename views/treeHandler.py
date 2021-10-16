import view
import wx
import locale


if __name__ == "__main__":
    app = wx.App(False)
    asis = view.Launcher(None)

    locale.setlocale(locale.LC_ALL, '')
    app.MainLoop()
