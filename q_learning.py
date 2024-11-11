from constants.constants import *
from game import set_initial_state
import utils.dice_utils as dice_utils
import utils.q_utils as q_utils
import numpy as np

TURNS = 13

current_turn = 0
dice, keep_dice, state, dice_rolls = set_initial_state()

def init_q_table() -> dict:
    Q = {
        # zaruri masluite >:)
        (1,2,3,4,5): {
            (0,0,0,0,1): 0,
            (0,0,0,1,0): 0,
            # ...
        },
        #...
        # din SCORE_ROWS
        0: {
            (0, 0, 0, 0, 1): 0,
            (0, 0, 0, 1, 0): 0,
            # ...
        },
        1: {
            (0, 0, 0, 0, 1): 0,
            (0, 0, 0, 1, 0): 0,
            # ...
        },
        #...
        14: {
            (0, 0, 0, 0, 1): 0,
            (0, 0, 0, 1, 0): 0,
            # ...
        }
    }
    # return Q
    # TODO: ce-i mai sus ^
    pass

def choose_action(sorted_dice, remaining_rolls) -> tuple[int,...] | int:
    global state
    # TODO: pentru a = sorted_dice
    # daca remaining_rolls == 0
    #     alege actiune din SCORE_ROWS cu valoare maxima pentru zarurile curente, daca nu a completat
    # altfel
    #     alege de peste tot, la SOCRE_ROWS fiind aceleasi consideratii de mai sus
    if remaining_rolls == 0:
        return np.random.choice(SCORE_ROWS)
    else:
        choice = np.random.randint(1, 32)
        # TODO: convert to tuple
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
