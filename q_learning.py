from constants.constants import *
from game import set_initial_state
import utils.dice_utils as dice_utils
import utils.q_utils as q_utils
import numpy as np
import random

TURNS = 13

current_turn = 0
dice, keep_dice, state, dice_rolls = set_initial_state()

def init_q_table() -> dict:
    dice_combinations = [(a, b, c, d, e) for a in range(1, 7) for b in range(a, 7) for c in range(b, 7) for d in range(c, 7) for e in range(d, 7)]
    choices = [(a, b, c, d, e) for a in range(2) for b in range(2) for c in range(2) for d in range(2) for e in range(2)][1:] # exclude 0,0,0,0,0 since it basically means rolling all dice

    Q = {}
    for comb in dice_combinations:
        Q[comb] = {}

        for choice in choices:
            Q[comb][choice] = 0

        for row in SCORE_ROWS:
            Q[comb][row] = 0
    
    return Q
    
def choose_action(sorted_dice, remaining_rolls, Q: dict) -> tuple[int,...] | int:
    global state

    if remaining_rolls == 0:
        available_actions = [row for row in SCORE_ROWS if state['points_table'][0][row] == -1]
        best_action = max(available_actions, key=lambda action: Q[sorted_dice][action])
        return best_action
    else:
        if random.random() < 0.4:
            choice = random.randint(1, 31)
            return tuple(int(x) for x in f"{choice:05b}")
        else:
            best_choice = max(Q[sorted_dice], key=Q[sorted_dice].get)
            if isinstance(best_choice, int):
                return best_choice
            else:
                choice = random.randint(1, 31)
                return tuple(int(bit) for bit in f"{choice:05b}")


def update_q_value(sorted_dice, action):
    # TODO: update Q value
    # momentan rewards random/arbitrare
    pass

def episode():
    global current_turn, dice, keep_dice, state, dice_rolls
    while current_turn < TURNS:
        remaining_rolls = 2
        dice = dice_utils.dice_roll(len(dice))
        sorted_dice = sorted(dice + keep_dice)
        action = choose_action(sorted_dice, remaining_rolls)
        while isinstance(action, tuple) and remaining_rolls > 0:
            #print("Rolling dice",action)
            sorted_dice = sorted(dice + keep_dice)
            dice, keep_dice = dice_utils.choose_dice_q(list(action), sorted_dice)
            update_q_value(sorted_dice, action)
            sorted_dice = sorted(dice + keep_dice)
            remaining_rolls -= 1
            action = choose_action(sorted_dice, remaining_rolls)
        else:
            #print("Updating score")
            q_utils.update_score(state, action, 0, dice, keep_dice)
            sorted_dice = sorted(dice + keep_dice)
            update_q_value(sorted_dice, action)
        current_turn += 1

scores = []

# for i in range(10_000):
#     episode()
#     scores.append(state['points_table'][0][SCORE_ROW])
#     current_turn = 0
#     dice, keep_dice, state, dice_rolls = set_initial_state()
