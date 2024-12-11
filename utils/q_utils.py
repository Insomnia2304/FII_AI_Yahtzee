import math

from constants.constants import *
from utils import dice_utils
import numpy as np

TURNS = 13

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

# def get_potential_dices(dice: tuple[int, ...], action: tuple[int, ...]):
#     potential_dices = []
#     keep_dice, reroll_dice = dice_utils.choose_dice_q(list(action), list(dice))
#     dice_combinations = [(a, b, c, d, e) for a in range(1, 7) for b in range(a, 7) for c in range(b, 7) for d in
#                          range(c, 7) for e in range(d, 7)]
#     for dice_combination in dice_combinations:
#         ok = True
#         reroll_count = [i for i in range(5) if action[i] == 1]
#         for index in list(action):
#             if index == 1 and dice_combination.index(dice_combination[index]) not in reroll_dice:
#                 ok = False
#                 break
#         if ok:
#             for i in range(math.factorial(len(reroll_count))):
#                 potential_dices.append(dice_combination)
#     return potential_dices


def get_reward(
        state: dict,
        dice: tuple[int, ...],
        action,
        old_scores: dict,
        new_scores: dict,
        remaining_rolls: int,
        new_dice: tuple[int, ...],
        score=-1
) -> float:

    # if action is a score row
    if isinstance(action, int):
        if score != -1:
            row = action
            if score == 0:
                # penalizam daca a scorat prea devreme 0 + penalty pt chance
                if row in [YAHTZEE_ROW, LARGE_STRAIGHT_ROW, FULL_HOUSE_ROW,14]:
                    if state['round_no'] <= TURNS // 2:
                        return -20
                    else:
                        potential_score = dice_utils.validate_choice(list(dice), row)
                        return -5 if potential_score == 0 else -10
                else:
                    return -2

            # daca a pus yahtzee large sau full house reward extra
            reward = score
            if row in [YAHTZEE_ROW, LARGE_STRAIGHT_ROW, FULL_HOUSE_ROW]:
                reward += 10

            # daca a facut bonus
            if row <= 5 and state['points_table'][1][SUM_ROW] + score >= 63:
                reward += 15
            return reward

    # scor average pentru zarurile noi - zarurile vechi
    # penalizare daca "a stricat" zaruri bune
    incomplete_rows = [row for row in SCORE_ROWS if state['points_table'][1][row] == -1]
    old_avg_score = np.mean([dice_utils.validate_choice(list(dice), row) for row in incomplete_rows])
    new_avg_score = np.mean([dice_utils.validate_choice(list(new_dice),row) for row in incomplete_rows])
    reward = new_avg_score - old_avg_score

    # penalizare daca a ramas fara rolls si a "stricat" zaruri bune
    if remaining_rolls == 0:
        reward -= 10 if new_avg_score < old_avg_score else 5
    else:
        reward += 10 if new_avg_score > old_avg_score else -5

    for row in incomplete_rows:
        if row in [YAHTZEE_ROW, LARGE_STRAIGHT_ROW, FULL_HOUSE_ROW]:
            potential_score = dice_utils.validate_choice(list(dice), row)
            if potential_score > 0:
                reward += 10

    return reward
