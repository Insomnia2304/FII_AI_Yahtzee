import numpy as np

import wx
import wx.grid
import constants.constants as uic
import game
from game import update_score
from game_history import GameHistoryFrame
from utils import dice_utils
from utils.gui_utils import alert_user

dice, keep_dice, state, dice_rolls = game.set_initial_state()


class MyFrame(wx.Frame):
    def reset_table(self):
        for i in range(len(uic.SCORE_ROWS)):
            for j in range(2):
                if state['points_table'][j][i] == -1:
                    self.grid.SetCellValue(i, j, '')
                self.grid.SetCellValue(uic.SUM_ROW, j, str(state['points_table'][j][uic.SUM_ROW]))
                self.grid.SetCellValue(uic.BONUS_ROW, j, str(state['points_table'][j][uic.BONUS_ROW]))
                self.grid.SetCellValue(uic.SCORE_ROW, j, str(state['points_table'][j][uic.SCORE_ROW]))
    def make_table(self):
        self.grid.CreateGrid(len(uic.POINTS_TABLE_LABELS), 2)
        self.grid.SetDefaultCellAlignment(horiz=wx.ALIGN_CENTRE, vert=wx.ALIGN_CENTRE)
        self.grid.RowLabelSize = 150

        self.grid.SetColLabelValue(0, "You")
        self.grid.SetColLabelValue(1, "AI")
        [self.grid.SetRowLabelValue(i, uic.POINTS_TABLE_LABELS[i]) for i in range(len(uic.POINTS_TABLE_LABELS))]
        self.reset_table()

        self.grid.EnableDragColSize(False)
        self.grid.EnableDragRowSize(False)

        for row in range(len(uic.POINTS_TABLE_LABELS)):
            for col in range(2):
                self.grid.SetReadOnly(row, col, True)

        for col in range(2):
            self.grid.SetCellBackgroundColour(uic.SUM_ROW, col, wx.Colour(210, 248, 210))
            self.grid.SetCellBackgroundColour(uic.BONUS_ROW, col, wx.Colour(210, 248, 210))
            self.grid.SetCellBackgroundColour(uic.SCORE_ROW, col, wx.Colour(177, 156, 217))

            self.grid.SetCellValue(uic.SUM_ROW, col, str(state['points_table'][col][uic.SUM_ROW]))
            self.grid.SetCellValue(uic.BONUS_ROW, col, str(state['points_table'][col][uic.BONUS_ROW]))
            self.grid.SetCellValue(uic.SCORE_ROW, col, str(state['points_table'][col][uic.SCORE_ROW]))

        self.grid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.on_cell_select)
        self.grid.Bind(wx.EVT_KEY_DOWN, self.on_key_press)



    def __init__(self, *args, **kw):
        super(MyFrame, self).__init__(*args, **kw)

        self.panel = wx.Panel(self)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)

        vbox1 = wx.BoxSizer(wx.VERTICAL)

        menu = wx.MenuBar()
        game_menu = wx.Menu()
        new_game = game_menu.Append(wx.ID_ANY, "New Game", "Start a new game")
        self.Bind(wx.EVT_MENU, self.on_new_game, new_game)
        game_history = game_menu.Append(wx.ID_ANY, "Game History", "View game history")
        self.Bind(wx.EVT_MENU, self.on_game_history, game_history)
        menu.Append(game_menu, "Game")
        self.SetMenuBar(menu)

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
            alert_user(
                f"Game Over!\nYou: {state['points_table'][0][uic.SCORE_ROW]}\nAI: {state['points_table'][1][uic.SCORE_ROW]}")
            self.reset_game()
            return
        dice = [1, 2, 3, 4, 5]
        keep_dice = []
        self.update_dice_container(self.dice_container, dice)
        self.update_dice_container(self.keep_dice_container, keep_dice, keep=True)
        dice_rolls = -1

        if state['round_no'] % 2 == 0:
            self.game_info.Label = "It's your turn"
        else:
            self.game_info.Label = "It's AI's turn"
            self.ai_move()
        self.vbox2.Layout()

    def ai_move(self):
        global dice, keep_dice

        roll_counts = np.random.randint(1, 4)
        for i in range(roll_counts):
            wx.CallLater(uic.AI_SLEEP_TIME * (i + 1), self.roll_dice_for_ai)

        # Delay the score update until after all rolls are complete
        choice = np.random.choice([index for index in uic.SCORE_ROWS if state['points_table'][1][index] == -1])
        wx.CallLater(uic.AI_SLEEP_TIME * (roll_counts + 1), lambda:
        game.update_score(state, self, choice, 1, dice, keep_dice))

    def roll_dice_for_ai(self):
        global dice, keep_dice

        dice = dice_utils.dice_roll(len(dice))
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
        if row not in uic.SCORE_ROWS:
            return
        if state['points_table'][0][row] != -1:
            alert_user("You have already chosen this category")
            return
        game.undisplay_potential_scores(state, self)
        update_score(state, self, row, 0, dice, keep_dice)
        event.Skip()

    def reset_game(self):
        global dice, keep_dice, state, dice_rolls
        print('Resetting game')
        dice, keep_dice, state, dice_rolls = game.set_initial_state()
        print(state['points_table'])
        self.update_dice_container(self.dice_container, dice)
        self.update_dice_container(self.keep_dice_container, keep_dice, keep=True)
        self.game_info.Label = "It's your turn"
        game.undisplay_potential_scores(state, self)
        self.reset_table()
        self.vbox2.Layout()

    def on_new_game(self, event):
        self.reset_game()
        event.Skip()

    def on_game_history(self, event):
        history_frame = GameHistoryFrame()
        history_frame.Show()
        event.Skip()

    def update_dice(self, die, is_keep):
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
            self.update_dice(die, is_keep)

    def on_roll_button(self, event):
        global dice, dice_rolls
        if state['round_no'] % 2 == 1:
            return
        if dice_rolls > 1:
            alert_user("You have already rolled the dice 2 times")
            return

        dice = dice_utils.dice_roll(len(dice))
        self.update_dice_container(self.dice_container, dice)
        dice_rolls += 1

        game.display_potential_scores(state, self, dice, keep_dice)
        self.game_info.Label = f"You can roll the dice {2 - dice_rolls} more times" if dice_rolls < 2 else "Please choose a category"
        self.vbox2.Layout()
        event.Skip()

    def on_key_press(self, event):
        match event.KeyCode:
            case 82:  # R key
                self.on_roll_button(event)
            case _:
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
