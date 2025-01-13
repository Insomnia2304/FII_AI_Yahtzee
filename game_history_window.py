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
    return fig

def get_stats(history):
    scores = []
    wins = []
    bonuses = []
    for entry in history:
        scores.append(entry['your_score'])
        if entry['your_score'] > entry['ai_score']:
            wins.append(1)
        else:
            wins.append(0)
        bonuses.append(1 if entry['sum_bonus'] > 0 else 0)
    average_score = sum(scores) / len(scores)
    win_rate = sum(wins) / len(wins)
    bonus_rate = sum(bonuses) / len(bonuses)
    return f"Your statistics:\nAverage score: {average_score:.2f}\nWin rate: {win_rate:.2f}\nBonuses percentage: {bonus_rate:.2f}"

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
        game_list.InsertColumn(0, 'Your score', width=175)
        game_list.InsertColumn(1, 'AI score', width=175)
        game_list.InsertColumn(2, 'First Half Bonus', width=175)
        game_list.InsertColumn(3, 'Date', width=175)

        for entry in history:
            index = game_list.InsertItem(game_list.GetItemCount(), str(entry['your_score']))
            game_list.SetItem(index, 1, str(entry['ai_score']))
            game_list.SetItem(index, 2, str(entry['sum_bonus']))
            game_list.SetItem(index, 3, entry['date'])

        plot = FigureCanvas(panel,-1,gen_plot(history))
        plot.SetSize(width=80, height=80)


        stats_text = get_stats(history)
        stats = wx.StaticText(panel, label=stats_text)

        hbox.Add(plot, border=10)
        hbox.Add(stats, flag=wx.LEFT | wx.CENTER, border=10)

        vbox.Add(history_text, flag=wx.ALL | wx.CENTER, border=10)
        vbox.Add(game_list, flag=wx.EXPAND | wx.ALL, border=10)
        vbox.Add(hbox, flag=wx.CENTER | wx.BOTTOM, border=10)

        panel.SetSizer(vbox)
        self.SetSize((800, 600))
        self.SetTitle('Game History')
        self.Centre()