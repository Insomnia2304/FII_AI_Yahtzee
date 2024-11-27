import math

from constants.constants import *
from utils import dice_utils
import numpy as np


def update_score(state, row, player, dice, keep_dice):
    total_dice = dice + keep_dice

    # multiple YAHTZEEs
    joker = upper_side_completed = False
    if len(set(total_dice)) == 1 and state['points_table'][player][YAHTZEE_ROW] != -1:
        joker = True
        if state['points_table'][player][YAHTZEE_ROW] != 0:
            state['points_table'][player][YAHTZEE_ROW] += 100
            state['points_table'][player][SCORE_ROW] += 100
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

    return score

def get_reward(dice: tuple[int,...], score=-1) -> float:
    if score != -1:
        return score

    if score == 0:
        return -5

    potential_scores = []
    for row in SCORE_ROWS:
        potential_scores.append(dice_utils.validate_choice(list(dice), row))

    reward = np.mean(potential_scores)
    if math.isnan(reward):
        print(potential_scores)
        print("NAN")

    return reward
