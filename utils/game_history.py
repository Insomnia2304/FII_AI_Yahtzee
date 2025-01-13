import json


def add_to_history(game_history, your_score, ai_score, sum_bonus, date):
    game_history.append({
        'your_score': your_score,
        'ai_score': ai_score,
        'sum_bonus': sum_bonus,
        'date': date
    })

def get_history(path='game_history.json'):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_history(game_history, path='game_history.json'):
    with open(path, 'w') as f:
        json.dump(game_history, f)