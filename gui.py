import wx
import wx.grid
import constants.constants as uic
from utils import dice_utils

dice = [1,2,3,4,5]
keep_dice = []

class MyFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(MyFrame, self).__init__(*args, **kw)

        self.panel = wx.Panel(self)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)

        vbox1 = wx.BoxSizer(wx.VERTICAL)
    
        grid = wx.grid.Grid(self.panel)
        grid.CreateGrid(13, 2)
        grid.RowLabelSize = 150 

        grid.SetColLabelValue(0, "You")
        grid.SetColLabelValue(1, "AI")
        [grid.SetRowLabelValue(i, uic.points_table[i]) for i in range(13)]

        grid.EnableDragColSize(False)
        grid.EnableDragRowSize(False)

        for row in range(13):
            for col in range(2):
                grid.SetReadOnly(row, col, True)

        grid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.on_cell_select)

        vbox1.Add(grid, proportion=1, flag=wx.CENTER, border=10)  

        self.vbox2 = wx.BoxSizer(wx.VERTICAL)
        
        self.label1 = wx.StaticText(self.panel, label="Dice:")
        self.dice_container = wx.BoxSizer(wx.HORIZONTAL)
        self.dice_container.SetMinSize((300,70))
        self.update_dice_container(self.dice_container, dice)

        self.label2 = wx.StaticText(self.panel, label="Keep Dice:")
        self.keep_dice_container = wx.BoxSizer(wx.HORIZONTAL)
        self.keep_dice_container.SetMinSize((300,70))
        self.update_dice_container(self.keep_dice_container, keep_dice, keep=True)
       
        self.roll_button = wx.Button(self.panel, label='Roll Dice')
        self.roll_button.Bind(wx.EVT_BUTTON, self.on_roll_button)

        self.vbox2.AddMany([
            (self.label1, 0, wx.CENTER, 5),
            (self.dice_container, 0, wx.CENTER, 5),
            (self.label2, 0, wx.CENTER, 5),
            (self.keep_dice_container, 0, wx.CENTER, 5),
            (self.roll_button, 0, wx.CENTER, 5)
        ])

        self.hbox.Add(vbox1, proportion=1, flag=wx.CENTER, border=30)
        self.hbox.Add(self.vbox2, proportion=1, flag=wx.CENTER, border=30)

        self.panel.SetSizer(self.hbox)

        self.SetSize((1024, 768))
        self.SetMinSize((1024, 768))
        self.SetMaxSize((1024, 768))
        self.SetTitle('Yahtzee')
        self.Centre()

    def update_dice_container(self, container: wx.BoxSizer, dice: list[int],keep=False):
        container.Clear(True)
        if(len(dice) == 0):
            container.AddSpacer(70)
        else:
            for i, die in enumerate(dice):
                image = wx.Image(f"img/dice_{die}.png", wx.BITMAP_TYPE_ANY).Scale(50, 50)
                bitmap = wx.Bitmap(image)
                static_bitmap = wx.StaticBitmap(self.panel, bitmap=bitmap)
                static_bitmap.Bind(wx.EVT_LEFT_DOWN, 
                                    lambda event, die=die: self.on_image_click(event, die, keep))
                container.Add(static_bitmap, 0, wx.CENTER, 5)
                if i != len(dice) - 1:
                    container.AddSpacer(10)
        container.Layout()

    def on_cell_select(self, event):
        print(event.GetRow(), event.GetCol())
        event.Skip()

    def on_image_click(self, event, die, is_keep):
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

    def on_roll_button(self, event):
        global dice
        dice = dice_utils.dice_roll(len(dice))
        self.update_dice_container(self.dice_container, dice)
        event.Skip()

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None)
        frame.Show(True)
        return True

if __name__ == '__main__':
    app = MyApp(False)
    app.MainLoop()