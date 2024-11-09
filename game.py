from constants.constants import *
from utils import dice_utils, gui_utils
import wx
import copy


def set_initial_state():
    state = copy.deepcopy(initial_state)
    dice = [1, 2, 3, 4, 5]
    keep_dice = []
    dice_rolls = -1
    return dice, keep_dice, state, dice_rolls


def is_final_state(state) -> bool:
    return state['round_no'] == 26


def update_score(state, game, row, player, dice, keep_dice):
    total_dice = dice + keep_dice

    # multiple YAHTZEEs
    joker = upper_side_completed = False
    if len(set(total_dice)) == 1 and state['points_table'][player][YAHTZEE_ROW] != -1:
        joker = True
        if state['points_table'][player][YAHTZEE_ROW] != 0:
            state['points_table'][player][YAHTZEE_ROW] += 100
            state['points_table'][player][SCORE_ROW] += 100
            game.grid.SetCellValue(YAHTZEE_ROW, player, str(state['points_table'][player][YAHTZEE_ROW]))
        if state['points_table'][player][total_dice[0]-1] != -1:
            upper_side_completed = True

    score = dice_utils.validate_choice(total_dice, row, joker=joker, upper_side_completed=upper_side_completed)
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

    joker = upper_side_completed = False
    if len(set(dice)) == 1 and state['points_table'][0][YAHTZEE_ROW] != -1:
        joker = True
        if state['points_table'][0][dice[0]-1] != -1:
            upper_side_completed = True

    for row in SCORE_ROWS:
        if state['points_table'][0][row] == -1:
            game.grid.SetCellValue(row, 0, str(dice_utils.validate_choice(total_dice, row, joker=joker, upper_side_completed=upper_side_completed)))
            game.grid.SetCellTextColour(row, 0, wx.RED)


def undisplay_potential_scores(state, game):
    for row in SCORE_ROWS:
        if state['points_table'][0][row] == -1:
            game.grid.SetCellValue(row, 0, "")
            game.grid.SetCellTextColour(row, 0, wx.BLACK)
