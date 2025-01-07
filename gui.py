import random
import wx
import wx.grid
import constants.constants as uic
import game
from game import update_score
from game_history import GameHistoryFrame
from utils import dice_utils
from utils.gui_utils import alert_user
import pickle
from q_learning import choose_action

dice, keep_dice, state, dice_rolls = game.set_initial_state()

with open('q_table.pkl', 'rb') as f:
    Q = pickle.load(f)

print(Q.keys())

class MyFrame(wx.Frame):
    def reset_table(self):
        for i in uic.SCORE_ROWS:
            for j in range(2):
                if state['points_table'][j][i] == -1:
                    self.grid.SetCellValue(i, j, '')
        for j in range(2):
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

        lighted_box_image = wx.Image("./img/hint.png", wx.BITMAP_TYPE_ANY).Scale(35, 35)
        self.tip_button = wx.BitmapButton(self.panel, bitmap=wx.Bitmap(lighted_box_image), pos=(20, 20))
        self.tip_button.Bind(wx.EVT_BUTTON, self.on_tip_button)

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

        self.tip_opened = False
        self.tip_panel = None
        self.tip_text = None

    def on_tip_button(self, event):
        self.tip_opened = not self.tip_opened
        self.show_tip()

    def show_tip(self):
        print(self.tip_opened)
        if not self.tip_opened:
            if self.tip_panel:
                self.tip_panel.Hide()
            return

        if dice_rolls == -1:
            tip = "You haven't even rolled the dice, yet you want a tip?"
        else:
            sorted_dice = sorted(dice + keep_dice)
            action = choose_action(tuple(sorted_dice), 2 - dice_rolls, Q, state, player=0)
            print(action)

            if isinstance(action, tuple):
                if sorted_dice.count(0) == 5:
                    tip = 'You couldn\'t have rolled a worse hand. Just roll again all of them.'
                else:
                    to_roll = []
                    to_keep = []
                    for i in range(len(sorted_dice)):
                        if action[i] == 0:
                            to_roll.append(sorted_dice[i])
                        else:
                            to_keep.append(sorted_dice[i])
                    tip = f'Just roll again {"the " if len(to_roll) == 1 else ""}{to_roll[0]}'
                    for die in to_roll[1:-1]:
                        tip += f', {die}'
                    if len(to_roll) > 1:
                        tip += f' and {to_roll[-1]}'
                    tip += '.\n'

                    tip += f'(Only keep {"the " if len(to_keep) == 1 else ""}{to_keep[0]}'
                    for die in to_keep[1:-1]:
                        tip += f', {die}'
                    if len(to_keep) > 1:
                        tip += f' and {to_keep[-1]}'
                    tip += ')'
            else:
                tip = f'Unless you want to lose, you should score {uic.POINTS_TABLE_LABELS[action]}.'

        if not self.tip_panel:
            self.tip_panel = wx.Panel(self.panel, pos=(80, 20), size=(900, 100))
            self.tip_panel.SetBackgroundColour(wx.Colour(255, 255, 255))

            self.tip_text = wx.TextCtrl(
                self.tip_panel,
                value=tip,
                pos=(10, 10),
                size=(880, 80),
                style=wx.TE_MULTILINE | wx.TE_WORDWRAP | wx.TE_READONLY | wx.BORDER_NONE
            )
            self.tip_text.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            self.tip_text.SetForegroundColour(wx.Colour(0, 0, 0))
            self.tip_text.SetBackgroundColour(wx.Colour(255, 255, 255))
        else:
            self.tip_text.SetValue(tip)

        self.tip_panel.Show()
        self.panel.Layout()


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
        global dice, keep_dice, dice_rolls

        if uic.AI_SLEEP_TIME == 0:
            self.roll_dice_for_ai()
        else:
            wx.CallLater(uic.AI_SLEEP_TIME, self.roll_dice_for_ai)


    def roll_dice_for_ai(self):
        global dice, keep_dice, dice_rolls, state, Q
        dice_rolls += 1

        dice = dice_utils.dice_roll(len(dice))

        sorted_dice = sorted(dice + keep_dice)
        action = choose_action(tuple(sorted_dice), 2 - dice_rolls, Q, state)
        print(action)
        if isinstance(action, tuple):
            dice, keep_dice = dice_utils.choose_dice_q(list(action), sorted_dice)
            wx.CallLater(uic.AI_SLEEP_TIME, self.roll_dice_for_ai_2)
        else:
            wx.CallLater(uic.AI_SLEEP_TIME, update_score,state, self, action, 1, dice, keep_dice)

        self.update_dice_container(self.dice_container, dice)
        self.update_dice_container(self.keep_dice_container, keep_dice, keep=True)

    # pentru a putea arata cand AI-ul pastrează zaruri
    def roll_dice_for_ai_2(self):
        global dice, keep_dice, dice_rolls

        self.update_dice_container(self.dice_container, dice)
        self.update_dice_container(self.keep_dice_container, keep_dice, keep=True)

        wx.CallLater(uic.AI_SLEEP_TIME, self.roll_dice_for_ai)

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

        self.show_tip()
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
