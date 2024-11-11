POINTS_TABLE_LABELS = [
    "Ones",
    "Twos",
    "Threes",
    "Fours",
    "Fives",
    "Sixes",
    "SUM",
    "BONUS",
    "Three of a Kind",
    "Four of a Kind",
    "Full House",
    "Small Straight",
    "Large Straight",
    "Yahtzee",
    "Chance",
    "SCORE"
]

SCORE_ROWS = [0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14]

initial_state = {
    'round_no': 0,
    'points_table': [
        [-1, -1, -1, -1, -1, -1, 0, 0, -1, -1, -1, -1, -1, -1, -1, 0],
        [-1, -1, -1, -1, -1, -1, 0, 0, -1, -1, -1, -1, -1, -1, -1, 0]
    ]
}

SUM_ROW = 6
BONUS_ROW = 7
YAHTZEE_ROW = 13
SCORE_ROW = 15

# AI_SLEEP_TIME = 0  # ms
AI_SLEEP_TIME = 1250  # ms
