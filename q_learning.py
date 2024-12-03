import numpy as np
from constants.constants import *
from game import set_initial_state
import utils.dice_utils as dice_utils
import utils.q_utils as q_utils
import random
import matplotlib.pyplot as plt
import pickle

TURNS = 13
ALPHA = 0.05
DECAY_RATE = 0.95
DISCOUNT = 0.9
EXPLORATION_CHANCE = 0.9
EXPLORATION_CHANCE_DECAY = 0.9999
MIN_EXPLORATION_CHANCE = 0.05

current_turn = 0
dice, keep_dice, state, dice_rolls = set_initial_state()


def decay_exploration_rate():
    global EXPLORATION_CHANCE
    EXPLORATION_CHANCE = max(MIN_EXPLORATION_CHANCE, EXPLORATION_CHANCE * EXPLORATION_CHANCE_DECAY)


def int_to_tuple(choice: int) -> tuple[int, ...]:
    return tuple(int(x) for x in f"{choice:05b}")


def init_q_table() -> dict:
    dice_combinations = [(a, b, c, d, e) for a in range(1, 7) for b in range(a, 7) for c in range(b, 7) for d in range(c, 7) for e in range(d, 7)]
    choices = [(a, b, c, d, e) for a in range(2) for b in range(2) for c in range(2) for d in range(2) for e in range(2)][1:]  # exclude 0,0,0,0,0 since it basically means rolling all dice

    Q = {}
    for comb in dice_combinations:
        Q[comb] = {}

        for choice in choices:
            Q[comb][choice] = 0.01

        for row in SCORE_ROWS:
            Q[comb][row] = 0.01

    return Q


def choose_action(sorted_dice, remaining_rolls, Q: dict, state: dict, exploration_chance=0.0) -> tuple[int, ...] | int:
    if remaining_rolls == 0:
        available_actions = [row for row in SCORE_ROWS if state['points_table'][1][row] == -1]
        if np.random.rand() < exploration_chance:
            return random.choice(available_actions)
        else:
            return max(available_actions, key=lambda action: Q[sorted_dice][action])
    else:
        available_actions_dice = [int_to_tuple(choice) for choice in range(1, 31)]
        if np.random.rand() < exploration_chance:
            return random.choice(available_actions_dice)
        else:
            return max(available_actions_dice, key=lambda action: Q[sorted_dice][action])


def update_q_value(old_state: tuple[int, ...], new_state: tuple[int, ...], action: tuple[int, ...] | int, reward: float):
    global Q, DISCOUNT, ALPHA
    Q[old_state][action] += ALPHA * (reward + DISCOUNT * max(Q[new_state].values()) - Q[old_state][action])


Q = init_q_table()


def episode():
    global current_turn, dice, keep_dice, state, dice_rolls, EXPLORATION_CHANCE
    current_turn = 0
    dice, keep_dice, state, dice_rolls = set_initial_state()

    while current_turn < TURNS:
        remaining_rolls = 2
        dice = dice_utils.dice_roll(len(dice))
        sorted_dice = sorted(dice + keep_dice)
        action = choose_action(tuple(sorted_dice), remaining_rolls, Q, state, EXPLORATION_CHANCE)

        while isinstance(action, tuple) and remaining_rolls > 0:
            sorted_dice = sorted(dice + keep_dice)
            dice, keep_dice = dice_utils.choose_dice_q(list(action), sorted_dice)
            new_sorted_dice = sorted(dice + keep_dice)
            reward = q_utils.get_reward(state, tuple(new_sorted_dice), -1, state['points_table'][1], state['points_table'][1], remaining_rolls)
            update_q_value(tuple(sorted_dice), tuple(new_sorted_dice), action, reward)
            remaining_rolls -= 1
            action = choose_action(tuple(new_sorted_dice), remaining_rolls, Q, state, EXPLORATION_CHANCE)
        else:
            score = q_utils.update_score(state, action, 1, dice, keep_dice)
            sorted_dice = sorted(dice + keep_dice)
            reward = q_utils.get_reward(state, tuple(sorted_dice), action, state['points_table'][1], state['points_table'][1], remaining_rolls, score)
            update_q_value(tuple(sorted_dice), tuple(sorted_dice), action, reward)

        current_turn += 1


scores = []

if __name__ == "__main__":
    for i in range(20_000):
        episode()
        decay_exploration_rate()
        if EXPLORATION_CHANCE == 0:
            break
        print(f"Episode {i} completed")
        scores.append(state['points_table'][1][SCORE_ROW])

    plt.plot(scores)
    window_size = 500
    rolling_mean = np.convolve(scores, np.ones(window_size) / window_size, mode='valid')
    plt.plot(range(len(rolling_mean)), rolling_mean)
    plt.show()

    with open('q_table.pkl', 'wb') as file:
        pickle.dump(Q, file)
