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
    time.sleep(0.5)
    game = games.get(game_id)
    if not game:
        return

    if game['bot1_move'] is None:
        game['score'][1] += 1  # Bot 2 wins by default
        game["terminated"] = True
        game["message"] = "Bot 1 was disqualified due to timeout."
    elif game['bot2_move'] is None:
        game['score'][0] += 1  # Bot 1 wins by default
        game["terminated"] = True
        game["message"] = "Bot 2 was disqualified due to timeout."

@app.route('/play_round/<game_id>/<bot_id>', methods=['POST'])
def play_round(game_id, bot_id):
    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found!"}), 404

    move = request.json.get("move")
    if move not in moves_map:
        return jsonify({"error": "Invalid move!"}), 400

    if game['bot1_move'] is None and game['bot2_move'] is None:
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
        if diff in [-1, 2]:
            game['score'][0] += 1
        elif diff in [-2, 1]:
            game['score'][1] += 1
        game['round'] += 1
        game['history'].append((game['bot1_move'], game['bot2_move']))

        # Check if game is finished
        if game['round'] == game['num_rounds']:
            winner = "Draw" if game['score'][0] == game['score'][1] else ("Bot 1" if game['score'][0] > game['score'][1] else "Bot 2")
            result = {"message": f"Game over! Winner: {winner}", "score": game['score']}
            games.clear()
            return jsonify(result), 200

    return jsonify({"status": "Waiting for opponent"}), 200

if __name__ == '__main__':
    port = 5005
    app.run(debug=True, host='0.0.0.0', port=port)
