import math

import wx
import wx.grid
import constants.constants as uic
from utils import dice_utils
from utils.gui_utils import alert_user

dice = [1, 2, 3, 4, 5]
keep_dice = []

state = uic.initial_state
turns = -1

class MyFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(MyFrame, self).__init__(*args, **kw)

        self.panel = wx.Panel(self)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)

        vbox1 = wx.BoxSizer(wx.VERTICAL)

        self.grid = wx.grid.Grid(self.panel)
        self.grid.CreateGrid(14, 2)
        self.grid.RowLabelSize = 150

        self.grid.SetColLabelValue(0, "You")
        self.grid.SetColLabelValue(1, "AI")
        [self.grid.SetRowLabelValue(i, uic.points_table[i]) for i in range(14)]

        self.grid.EnableDragColSize(False)
        self.grid.EnableDragRowSize(False)

        for row in range(14):
            for col in range(2):
                self.grid.SetReadOnly(row, col, True)

        self.grid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.on_cell_select)

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
        global dice, keep_dice, state, turns
        state['round_no'] += 1
        if state['round_no'] == 26:
            scores = dice_utils.get_scores(state['points_table'])
            self.grid.SetCellValue(13, 0, str(scores[0]))
            self.grid.SetCellValue(13, 1, str(scores[1]))
            alert_user(f"Game Over!\nYou: {scores[0]}\nAI: {scores[1]}")
            return
        dice = [1, 2, 3, 4, 5]
        keep_dice = []
        self.update_dice_container(self.dice_container, dice)
        self.update_dice_container(self.keep_dice_container, keep_dice, keep=True)
        turns = -1
        if state['round_no'] % 2 == 0:
            self.game_info.Label = "It's your turn"
            self.vbox2.Layout()
        else:
            self.game_info.Label = "It's AI's turn"
            self.vbox2.Layout()
            self.ai_move()

    def ai_move(self):
        # TODO: implement AI random
        global dice, turns
        dice = dice_utils.dice_roll(5)
        print(dice)
        turns += 1
        self.update_dice_container(self.dice_container, dice)
        wx.CallLater(1250,lambda: self.update_score(math.floor(state['round_no'] / 2), 1))


    def update_score(self, row: int, player: int):
        global dice
        global keep_dice
        total_dice = dice + keep_dice
        score = dice_utils.validate_choice(total_dice, row)
        state['points_table'][player][row] = score
        self.grid.SetCellValue(row, player, str(score))
        self.next_round()

    def on_cell_select(self, event):
        row, col = event.GetRow(), event.GetCol()
        if row == 13 or state['round_no'] % 2 == 1:
            pass
        elif turns == -1:
            alert_user("Please roll the dice first")
        elif state['points_table'][0][row] != -1:
            alert_user("You have already chosen this category")
        elif 0 <= row < 13 and col == 0:
            self.update_score(row, col)
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
        if turns == -1:
            alert_user("Please roll the dice first")
        else:
            self.update_dice(die,is_keep)

    def on_roll_button(self, event):
        global dice, turns
        if state['round_no'] % 2 == 1:
            event.Skip()
            return
        if turns > 1:
            alert_user("You have already rolled the dice 2 times")
        else:
            dice = dice_utils.dice_roll(len(dice))
            self.update_dice_container(self.dice_container, dice)
            turns += 1
        self.game_info.Label = f"You can roll the dice {2 - turns} more times" if turns < 2 else "Please choose a category"
        self.vbox2.Layout()
        event.Skip()


class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None)
        frame.Show(True)
        return True


if __name__ == '__main__':
    app = MyApp(False)
    app.MainLoop()
