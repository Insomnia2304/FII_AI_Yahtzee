import numpy as np

import wx
import wx.grid
import constants.constants as uic
import game
from game import update_score
from utils import dice_utils
from utils.gui_utils import alert_user

dice, keep_dice, state, dice_rolls = game.set_initial_state()

class MyFrame(wx.Frame):
    def make_table(self):
        self.grid.CreateGrid(len(uic.points_table_labels), 2)
        self.grid.RowLabelSize = 150

        self.grid.SetColLabelValue(0, "You")
        self.grid.SetColLabelValue(1, "AI")
        [self.grid.SetRowLabelValue(i, uic.points_table_labels[i]) for i in range(len(uic.points_table_labels))]

        self.grid.EnableDragColSize(False)
        self.grid.EnableDragRowSize(False)

        for row in range(len(uic.points_table_labels)):
            for col in range(2):
                self.grid.SetReadOnly(row, col, True)

        self.grid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.on_cell_select)
    def __init__(self, *args, **kw):
        super(MyFrame, self).__init__(*args, **kw)

        self.panel = wx.Panel(self)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)

        vbox1 = wx.BoxSizer(wx.VERTICAL)

        self.grid = wx.grid.Grid(self.panel)
        self.make_table()
        vbox1.Add(self.grid, proportion=1, flag=wx.CENTER, border=10)

        self.vbox2 = wx.BoxSizer(wx.VERTICAL)

        self.label1 = wx.StaticText(self.panel, label="Dice:")
        self.dice_container = wx.BoxSizer(wx.HORIZONTAL)
        self.dice_container.SetMinSize((300, 70))
        self.update_dice_container(self.dice_container, dice)

        self.label2 = wx.StaticText(self.panel, label="Keep Dice:")
        self.keep_dice_container = wx.BoxSizer(wx.HORIZONTAL)
        self.keep_dice_container.SetMinSize((300, 70))
        self.update_dice_container(self.keep_dice_container, keep_dice, keep=True)

        self.roll_button = wx.Button(self.panel, label='Roll Dice')
        self.roll_button.Bind(wx.EVT_BUTTON, self.on_roll_button)

        self.game_info = wx.StaticText(self.panel, label="It's your turn")
        self.game_info.SetFont(
            wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName='Arial')
        )

        self.vbox2.AddMany([
            (self.label1, 0, wx.CENTER, 5),
            (self.dice_container, 0, wx.CENTER, 5),
            (self.label2, 0, wx.CENTER, 5),
            (self.keep_dice_container, 0, wx.CENTER, 5),
            (self.roll_button, 0, wx.CENTER, 5),
            (self.game_info, 0, wx.CENTER, 5)
        ])

        self.hbox.Add(vbox1, proportion=1, flag=wx.CENTER, border=30)
        self.hbox.Add(self.vbox2, proportion=1, flag=wx.CENTER, border=30)

        self.panel.SetSizer(self.hbox)

        self.SetSize((1024, 768))
        self.SetMinSize((1024, 768))
        self.SetMaxSize((1024, 768))
        self.SetTitle('Yahtzee')
        self.Centre()

    def update_dice_container(self, container: wx.BoxSizer, dice: list[int], keep=False):
        self.panel.Freeze()
        container.Clear(True)
        if len(dice) == 0:
            container.AddSpacer(70)
        else:
            for i, die in enumerate(dice):
                image = wx.Image(f"img/dice_{die}.png", wx.BITMAP_TYPE_ANY).Scale(50, 50)
                bitmap = wx.Bitmap(image)
                static_bitmap = wx.StaticBitmap(self.panel, bitmap=bitmap)
                if state['round_no'] % 2 == 0:
                    static_bitmap.Bind(wx.EVT_LEFT_DOWN,
                                   lambda event, val=die: self.on_image_click(event, val, keep))
                container.Add(static_bitmap, 0, wx.CENTER, 5)
                if i != len(dice) - 1:
                    container.AddSpacer(10)
        container.Layout()
        self.panel.Thaw()

    def next_round(self):
        global dice, keep_dice, state, dice_rolls
        state['round_no'] += 1
        if game.is_final_state(state):
            scores = game.get_scores(state['points_table'])
            self.grid.SetCellValue(13, 0, str(scores[0]))
            self.grid.SetCellValue(13, 1, str(scores[1]))
            alert_user(f"Game Over!\nYou: {scores[0]}\nAI: {scores[1]}")
            return
        dice = [1, 2, 3, 4, 5]
        keep_dice = []
        self.update_dice_container(self.dice_container, dice)
        self.update_dice_container(self.keep_dice_container, keep_dice, keep=True)
        dice_rolls = -1
        if state['round_no'] % 2 == 0:
            self.game_info.Label = "It's your turn"
            self.vbox2.Layout()
        else:
            self.game_info.Label = "It's AI's turn"
            self.vbox2.Layout()
            self.ai_move()

    def ai_move(self):
        global dice, keep_dice

        roll_counts = np.random.randint(1, 4)
        for i in range(roll_counts):
            wx.CallLater(1250 * (i + 1), self.roll_dice_for_ai)

        # Delay the score update until after all rolls are complete
        choice = np.random.choice([index for index in range(13) if state['points_table'][1][index] == -1])
        wx.CallLater(1250 * (roll_counts + 1), lambda:
                     game.update_score(state, self, choice, 1, dice, keep_dice))

    def roll_dice_for_ai(self):
        global dice, keep_dice
        dice, new = dice_utils.choose_dice(dice)
        keep_dice += new
        print(dice, keep_dice)

        self.update_dice_container(self.dice_container, dice)
        self.update_dice_container(self.keep_dice_container, keep_dice, keep=True)

    def on_cell_select(self, event):
        row, col = event.GetRow(), event.GetCol()
        if state['round_no'] % 2 == 1 or col != 0:
            return
        if dice_rolls == -1:
            alert_user("Please roll the dice first")
            return
        if row not in [0,1,2,3,4,5,8,9,10,11,12,13,14]:
            return
        if state['points_table'][0][row] != -1:
            alert_user("You have already chosen this category")
            return
        update_score(state, self, row, 0, dice, keep_dice)
        event.Skip()

    def update_dice(self,die,is_keep):
        global dice
        global keep_dice
        if is_keep:
            keep_dice.remove(die)
            print(keep_dice)
            dice.append(die)
            self.update_dice_container(self.dice_container, dice)
            self.update_dice_container(self.keep_dice_container, keep_dice, keep=True)
        else:
            dice.remove(die)
            print(dice)
            keep_dice.append(die)
            self.update_dice_container(self.dice_container, dice)
            self.update_dice_container(self.keep_dice_container, keep_dice, keep=True)

    def on_image_click(self, event, die, is_keep):
        if dice_rolls == -1:
            alert_user("Please roll the dice first")
        else:
            self.update_dice(die,is_keep)

    def on_roll_button(self, event):
        global dice, dice_rolls
        if state['round_no'] % 2 == 1:
            event.Skip()
            return
        if dice_rolls > 1:
            alert_user("You have already rolled the dice 2 times")
        else:
            dice = dice_utils.dice_roll(len(dice))
            self.update_dice_container(self.dice_container, dice)
            dice_rolls += 1
        self.game_info.Label = f"You can roll the dice {2 - dice_rolls} more times" if dice_rolls < 2 else "Please choose a category"
        self.vbox2.Layout()
        event.Skip()


class MyApp(wx.App):
    def __init__(self, redirect=False, filename=None, useBestVisual=False, clearSigInt=True):
        super().__init__(redirect, filename, useBestVisual, clearSigInt)
        self.frame = None

    def OnInit(self):
        self.frame = MyFrame(None)
        self.frame.Show(True)
        return True


if __name__ == '__main__':
    app = MyApp(False)
    app.MainLoop()
