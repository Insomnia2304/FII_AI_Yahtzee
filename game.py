from constants.constants import *
from utils import dice_utils, gui_utils
import wx

def set_initial_state():
    state = initial_state.copy()
    dice = [1, 2, 3, 4, 5]
    keep_dice = []
    dice_rolls = -1
    return dice, keep_dice, state, dice_rolls

def is_final_state(state) -> bool:
    return state['round_no'] == 26

def update_score(state, game, row, player, dice, keep_dice):
    total_dice = dice + keep_dice

    score = dice_utils.validate_choice(total_dice, row)
    state['points_table'][player][row] = score

    if 0 <= row <= 5:
        state['points_table'][player][SUM_ROW] += score
        if state['points_table'][player][SUM_ROW] >= 63:
            state['points_table'][player][BONUS_ROW] = 35
            state['points_table'][player][SCORE_ROW] += 35
            
    state['points_table'][player][SCORE_ROW] += score

    game.grid.SetCellValue(row, player, str(score))
    game.grid.SetCellValue(SUM_ROW, player, str(state['points_table'][player][SUM_ROW]))
    game.grid.SetCellValue(BONUS_ROW, player, str(state['points_table'][player][BONUS_ROW]))
    game.grid.SetCellValue(SCORE_ROW, player, str(state['points_table'][player][SCORE_ROW]))

    game.next_round()

def display_potential_scores(state, game, dice, keep_dice):
    total_dice = dice + keep_dice

    for row in SCORE_ROWS:
        if state['points_table'][0][row] == -1:
            game.grid.SetCellValue(row, 0, str(dice_utils.validate_choice(total_dice, row)))
            game.grid.SetCellTextColour(row, 0, wx.RED)

def undisplay_potential_scores(state, game):
    for row in SCORE_ROWS:
        if state['points_table'][0][row] == -1:
            game.grid.SetCellValue(row, 0, "")
            game.grid.SetCellTextColour(row, 0, wx.BLACK)
