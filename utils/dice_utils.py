import numpy as np


def dice_roll(no_of_dice: int) -> list[int]:
    # return [np.random.randint(1, 7)] * no_of_dice  # ATTENTION - LOADED DICE - Debugging purposes / Gambling addicts
    return np.random.randint(1, 7, no_of_dice).tolist()


def choose_dice(dice: list[int]) -> tuple[list[int], list[int]]:
    indexes = np.random.choice(range(len(dice)), np.random.randint(len(dice) + 1), replace=False)
    return [x for x in dice if dice.index(x) not in indexes], [x for x in dice if dice.index(x) in indexes]


def validate_choice(dice: list[int], choice: int, joker=False, upper_side_completed=True) -> int:
    if 0 <= choice <= 5:
        return dice.count(choice + 1) * (choice + 1)
    if joker is True and upper_side_completed is False:
        return 0
    match choice:
        case 8:  # Three of a kind
            return sum(dice) if dice.count(max(set(dice), key=dice.count)) >= 3 else 0
        case 9:  # Four of a kind
            return sum(dice) if dice.count(max(set(dice), key=dice.count)) >= 4 else 0
        case 10:  # Full house
            return 25 if len(set(dice)) == 2 and 2 <= dice.count(dice[0]) or joker is True <= 3 else 0
        case 11:  # Small straight
            return 30 if any(
                all(num in dice for num in seq) for seq in ([1, 2, 3, 4], [2, 3, 4, 5], [3, 4, 5, 6])) or joker is True else 0
        case 12:  # Large straight
            return 40 if sorted(dice) in [[1, 2, 3, 4, 5], [2, 3, 4, 5, 6]] or joker is True else 0
        case 13:  # Yahtzee
            return 50 if len(set(dice)) == 1 else 0
        case 14:  # Chance
            return sum(dice)
        case _:  # Invalid choice
            return -1
