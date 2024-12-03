import math

from constants.constants import *
from q_learning import TURNS
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
        if state['points_table'][player][total_dice[0] - 1] != -1:
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


def get_reward(
        state: dict,
        dice: tuple[int, ...],
        action: int,
        old_scores: dict,
        new_scores: dict,
        remaining_rolls: int,
        score=-1
) -> float:

    if score != -1:
        row = action - 31
        if score == 0:
            if row in ['YAHTZEE_ROW', 'LARGE_STRAIGHT_ROW', 'FULL_HOUSE_ROW']:
                if state['turn'] <= TURNS // 2:
                    return -20
                else:
                    potential_score = dice_utils.validate_choice(list(dice), row)
                    return -5 if potential_score == 0 else -10
            else:
                return -2

        reward = score
        if row in ['YAHTZEE_ROW', 'LARGE_STRAIGHT_ROW', 'FULL_HOUSE_ROW']:
            reward += 10
        if row <= 5 and state['points_table'][1][SUM_ROW] + score >= 63:
            reward += 15
        return reward

    incomplete_rows = [row for row in SCORE_ROWS if state['points_table'][1][row] == -1]
    old_avg_score = np.mean([old_scores[row] for row in incomplete_rows])
    new_avg_score = np.mean([new_scores[row] for row in incomplete_rows])
    reward = new_avg_score - old_avg_score

    if remaining_rolls == 0:
        reward -= 10 if new_avg_score < old_avg_score else 5
    else:
        reward += 10 if new_avg_score > old_avg_score else -5

    for row in incomplete_rows:
        if row in ['YAHTZEE_ROW', 'LARGE_STRAIGHT_ROW', 'FULL_HOUSE_ROW']:
            potential_score = dice_utils.validate_choice(list(dice), row)
            if potential_score > 0:
                reward += 10

    return reward
