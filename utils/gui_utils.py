import wx

def alert_user(message: str):
    dlg = wx.MessageDialog(None, message, "Yahtzee", wx.OK | wx.ICON_NONE)
    dlg.ShowModal()
    dlg.Destroy()