import wx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from utils.game_history import get_history

WIN_COLOUR = (230, 255, 230)
LOSE_COLOUR = (255, 230, 230)

def gen_plot(history):
    scores = []
    for entry in history:
        scores.append(entry['your_score'])
    fig, ax = plt.subplots()
    # change size of fig
    fig.set_size_inches(3, 3)
    ax.plot(scores)
    ax.set_facecolor('#f0f0f0')
    fig.set_facecolor('#f0f0f0')
    return fig

def get_stats(history):
    scores, wins, bonuses, yahtzees = [], [], [], []
    for entry in history:
        scores.append(entry['your_score'])
        if entry['your_score'] > entry['ai_score']:
            wins.append(1)
        else:
            wins.append(0)
        bonuses.append(1 if entry['sum_bonus'] > 0 else 0)
        yahtzees.append(entry['yahtzee_bonus']/50)
    average_score = sum(scores) / len(scores)
    win_rate = sum(wins) / len(wins)
    bonus_rate = sum(bonuses) / len(bonuses)
    yahtzees = int(sum(yahtzees))
    matches = len(scores)
    return (f"Your statistics:\nAverage score: {average_score:.2f}\nWin rate: "
            f"{win_rate:.2f}%\nBonuses percentage: {bonus_rate:.2f}%"), yahtzees, matches

class GameHistoryFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title='Game History', size=(400, 300))
        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        history = get_history()

        # Add content to the game history window here
        history_text = wx.StaticText(panel, label="Your game history:")
        game_list = wx.ListCtrl(panel, style=wx.LC_REPORT)
        game_list.InsertColumn(0, 'Your score', width=120)
        game_list.InsertColumn(1, 'AI score', width=120)
        game_list.InsertColumn(2, 'First Half Bonus', width=120)
        game_list.InsertColumn(3, 'Yahtzee', width=120)
        game_list.InsertColumn(4, 'Date', width=120)

        for entry in history:
            index = game_list.InsertItem(game_list.GetItemCount(), str(entry['your_score']))
            game_list.SetItem(index, 1, str(entry['ai_score']))
            game_list.SetItem(index, 2, str(entry['sum_bonus']))
            game_list.SetItem(index, 3, str(entry['yahtzee_bonus']))
            game_list.SetItem(index, 4, entry['date'])
            win = entry['your_score'] > entry['ai_score']
            if win:
                game_list.SetItemBackgroundColour(index, WIN_COLOUR)
            else:
                game_list.SetItemBackgroundColour(index, LOSE_COLOUR)

        plot = FigureCanvas(panel,-1,gen_plot(history))
        plot.SetSize(width=80, height=80)


        stats_text, yahtzees, matches = get_stats(history)
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

        stats = wx.StaticText(panel, label=stats_text)
        yahtzee = wx.StaticText(panel, label=f"In {matches} matches you got {yahtzees} yahtzees")
        stats.SetFont(font)
        yahtzee.SetFont(font)
        vbox_stats = wx.BoxSizer(wx.VERTICAL)

        vbox_stats.Add(stats, flag=wx.ALL | wx.CENTER, border=10)
        vbox_stats.Add(yahtzee, flag=wx.ALL | wx.CENTER, border=10)

        hbox.Add(plot, border=10)
        hbox.Add(vbox_stats, flag=wx.LEFT | wx.CENTER, border=10)

        vbox.Add(history_text, flag=wx.ALL | wx.CENTER, border=10)
        vbox.Add(game_list, flag=wx.EXPAND | wx.ALL, border=10)
        vbox.Add(hbox, flag=wx.CENTER | wx.BOTTOM, border=10)

        panel.SetSizer(vbox)
        self.SetSize((800, 600))
        self.SetTitle('Game History')
        self.Centre()