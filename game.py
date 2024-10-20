from constants.constants import *
from utils import dice_utils

def get_scores(state) -> list[int]:
    scores = []
    for i in range(2):
        scores[i] = state['first_half'][i] + state['second_half'][i] + state['bonus'][i]
    return scores

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
    game.grid.SetCellValue(row, player, str(score))
    if 0 <= row < 6:
        state['first_half'][player] += score
        if state['first_half'][player] >= 63:
            state['bonus'][player] = 35
    elif 6 <= row < 13:
        state['second_half'][player] += score
    game.next_round()
