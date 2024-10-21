points_table_labels = [
    "Ones",
    "Twos",
    "Threes",
    "Fours",
    "Fives",
    "Sixes",
    "BONUS",
    "SUM",
    "Three of a Kind",
    "Four of a Kind",
    "Full House",
    "Small Straight",
    "Large Straight",
    "Yahtzee",
    "Chance",
    "SCORE"
]

initial_state = {
    'round_no': 0,
    'points_table': [[-1,-1,-1,-1,-1,-1,0,0,-1,-1,-1,-1,-1,-1,-1,0], [-1,-1,-1,-1,-1,-1,0,0,-1,-1,-1,-1,-1,-1,-1,0]]
}

BONUS_ROW = 6
SUM_ROW = 7
SCORE_ROW = 15
