import numpy as np

def dice_roll(no_of_dice: int) -> list[int]:
    return np.random.randint(1, 7, no_of_dice).tolist()

def choose_dice(dice: list[int]) -> list[int]:
    indexes = np.random.choice(range(len(dice)), np.random.randint(len(dice)+1), replace=False)
    return [dice[i] for i in indexes]

def validate_choice(dice: list[int], choice: int) -> int:
    if 0 <= choice and choice <= 5:
        return dice.count(choice + 1) * (choice + 1)
    match choice:
        case 6: # Three of a kind
            return sum(dice) if dice.count(max(set(dice), key=dice.count)) >= 3 else 0
        case 7: # Four of a kind
            return sum(dice) if dice.count(max(set(dice), key=dice.count)) >= 4 else 0
        case 8: # Full house
            return 25 if len(set(dice)) == 2 and 2 <= dice.count(dice[0]) <= 3 else 0
        case 9: # Small straight
            return 30 if any(all(num in dice for num in seq) for seq in ([1, 2, 3, 4], [2, 3, 4, 5], [3, 4, 5, 6])) else 0
        case 10: # Large straight
            return 40 if sorted(dice) in [[1, 2, 3, 4, 5], [2, 3, 4, 5, 6]] else 0
        case 11: # Yahtzee
            return 50 if len(set(dice)) == 1 else 0
        case 12: # Chance
            return sum(dice)
        case _: # Invalid choice
            return -1

def get_scores(points_table: list[list[int]]) -> list[int]:
    ans = [0, 0]
    for i in range(2):
        ans[i] = sum([_ for _ in points_table[i] if _ != -1])
        ans[i] += 35 if sum(points_table[i][0:6]) >= 63 else 0
    return ans