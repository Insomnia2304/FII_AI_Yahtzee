import wx

class GameHistoryFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title='Game History', size=(400, 300))
        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Add content to the game history window here
        history_text = wx.StaticText(panel, label="Game History will be displayed here.")
        game_list = wx.ListCtrl(panel, style=wx.LC_REPORT)
        vbox.Add(history_text, flag=wx.ALL | wx.CENTER, border=10)
        vbox.Add(game_list, flag=wx.EXPAND | wx.ALL, border=10)

        panel.SetSizer(vbox)
        self.SetSize((800, 600))
        self.SetTitle('Game History')
        self.Centre()