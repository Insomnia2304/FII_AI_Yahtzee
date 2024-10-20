points_table_labels = [
    "Ones",
    "Twos",
    "Threes",
    "Fours",
    "Fives",
    "Sixes",
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
    'points_table': [[-1] * 13, [-1] * 13],
    'first_half': [0, 0], # ones - sixes
    'second_half': [0, 0], # three of a kind - chance
    'bonus': [0, 0] # bonus pentru 63+ la prima jumatate
}