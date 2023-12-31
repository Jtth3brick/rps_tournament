import random
import time
import threading
from flask import Flask, request, jsonify

app = Flask(__name__)

games = {}
moves_map = {"Rock": -1, "Paper": 0, "Scissors": 1}

def generate_bot_id():
    return str(random.randint(10000, 99999))

@app.route('/start_game', methods=['POST'])
def start_game():
    games.clear()  # Clear the games dictionary
    game_id = "1"  # We're assuming only one game at a time
    bot1_id = generate_bot_id()
    bot2_id = generate_bot_id()

    while bot1_id == bot2_id:
        bot2_id = generate_bot_id()

    num_rounds = request.json.get("num_rounds", 5)
    games[game_id] = {
        "bot1_id": bot1_id,
        "bot2_id": bot2_id,
        "bot1_move": None,
        "bot2_move": None,
        "round": 0,
        "score": [0, 0],
        "num_rounds": num_rounds,
        "history": []
    }

    return jsonify({
        "game_id": game_id,
        "bot1_id": bot1_id,
        "bot2_id": bot2_id,
        "message": "Game started!"
    }), 200

def check_moves_timeout(game_id):
    time.sleep(0.7)
    game = games.get(game_id)
    if not game:
        return

    if game['bot1_move'] is None and game['bot2_move'] is not None:
        game['score'][1] += 1  # Bot 2 wins by default
        game["terminated"] = True
        game["message"] = "Bot 1 was disqualified due to timeout."
    elif game['bot2_move'] is None and game['bot1_move'] is not None:
        game['score'][0] += 1  # Bot 1 wins by default
        game["terminated"] = True
        game["message"] = "Bot 2 was disqualified due to timeout."
    else:
        game['score'][0] = 0
        game['score'][1] = 0
        game["terminated"] = True
        game["message"] = "Both bots were disqualified due to timeout."


@app.route('/play_round/<game_id>/<bot_id>', methods=['POST'])
def play_round(game_id, bot_id):
    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found!"}), 404

    move = request.json.get("move")
    if move not in moves_map:
        return jsonify({"error": "Invalid move!"}), 400

    if game['round'] != 0 and game['bot1_move'] is None and game['bot2_move'] is None:
        threading.Thread(target=check_moves_timeout, args=(game_id,)).start()

    if bot_id == game['bot1_id']:
        game['bot1_move'] = move
    elif bot_id == game['bot2_id']:
        game['bot2_move'] = move
    else:
        return jsonify({"error": "Invalid Bot ID!"}), 404

    if game.get('terminated', False):
        return jsonify({"error": game["message"]}), 400

    if game['bot1_move'] and game['bot2_move']:
        diff = moves_map[game['bot1_move']] - moves_map[game['bot2_move']]
        result = "Draw"
        if diff in [-1, 2]:
            game['score'][0] += 1
            result = "Bot 1 Wins" if bot_id == game['bot1_id'] else "Bot 2 Wins"
        elif diff in [-2, 1]:
            game['score'][1] += 1
            result = "Bot 2 Wins" if bot_id == game['bot1_id'] else "Bot 1 Wins"
        game['round'] += 1
        game['history'].append((game['bot1_move'], game['bot2_move']))

        your_move = game['bot1_move'] if bot_id == game['bot1_id'] else game['bot2_move']
        opponent_move = game['bot2_move'] if bot_id == game['bot1_id'] else game['bot1_move']
        
        outcome = "Draw"
        if result == "Bot 1 Wins":
            outcome = "You win" if bot_id == game['bot1_id'] else "You lose"
        elif result == "Bot 2 Wins":
            outcome = "You win" if bot_id == game['bot2_id'] else "You lose"

        your_name = "Bot 1" if bot_id == game['bot1_id'] else "Bot 2"

        # Check if game is finished
        if game['round'] == game['num_rounds']:
            winner = "Draw" if game['score'][0] == game['score'][1] else ("Bot 1" if game['score'][0] > game['score'][1] else "Bot 2")
            final_result = {"message": f"Game over! Winner: {winner}", "score": game['score']}
            games.clear()
            return jsonify(final_result), 200

        round_result = {
            "your_name": your_name,
            "outcome": outcome,
            "your_move": your_move,
            "opponent_move": opponent_move,
            "score": game['score']
        }
        return jsonify(round_result), 200

    return jsonify({"status": "Waiting for opponent"}), 200


if __name__ == '__main__':
    port = 5005
    app.run(debug=True, host='0.0.0.0', port=port)
