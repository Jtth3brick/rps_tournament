import random
from flask import Flask, request, jsonify

app = Flask(__name__)

games = {}
moves_map = {"Rock": -1, "Paper": 0, "Scissors": 1}

def generate_bot_id():
    return str(random.randint(10000, 99999))

@app.route('/start_game', methods=['POST'])
def start_game():
    game_id = str(len(games) + 1)
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
    
    print(f"Expected Bot IDs for game {game_id}: Bot 1: {bot1_id}, Bot 2: {bot2_id}")

    return jsonify({
        "game_id": game_id,
        "bot1_id": bot1_id,
        "bot2_id": bot2_id,
        "message": "Game started!"
    }), 200

@app.route('/play_round/<game_id>/<bot_id>', methods=['POST'])
def play_round(game_id, bot_id):
    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found!"}), 404
    
    move = request.json.get("move")
    
    if move not in moves_map:
        return jsonify({"error": "Invalid move!"}), 400

    if bot_id == game['bot1_id']:
        game['bot1_move'] = move
        print(f"Received move {move} from Bot 1 ({bot_id})")
    elif bot_id == game['bot2_id']:
        game['bot2_move'] = move
        print(f"Received move {move} from Bot 2 ({bot_id})")
    else:
        return jsonify({"error": "Invalid Bot ID!"}), 404

    if game['bot1_move'] is None:
        print(f"Waiting for Bot 1 ({game['bot1_id']}) to make a move...")
        return jsonify({"status": "Waiting for opponent"}), 200
    if game['bot2_move'] is None:
        print(f"Waiting for Bot 2 ({game['bot2_id']}) to make a move...")
        return jsonify({"status": "Waiting for opponent"}), 200

    # Once both moves are received, compute outcome
    result = (moves_map[game['bot1_move']] - moves_map[game['bot2_move']]) % 3
    if result == 0:
        outcome = "draw"
    elif result == 1:
        outcome = "lose"
        game["score"][1] += 1
    else:
        outcome = "win"
        game["score"][0] += 1
    
    game["history"].append((game['bot1_move'], game['bot2_move'], outcome))
    game["round"] += 1

    game['bot1_move'] = None  # Reset moves for next round
    game['bot2_move'] = None

    if game["round"] >= game["num_rounds"]:
        del games[game_id]
        return jsonify({"game_over": True, "history": game["history"], "score": game["score"]}), 200
    
    return jsonify({"opponent_move": move, "outcome": outcome}), 200

if __name__ == '__main__':
    port = 5005
    host_ip = "127.0.0.1"
    print(f"\nServer is starting on http://{host_ip}:{port}")
    print("\nConnection Instructions:")
    print(f"1. Start a new game: POST http://{host_ip}:{port}/start_game with optional JSON body {{\"num_rounds\": <desired_number_of_rounds>}}")
    print(f"2. Play a round: POST http://{host_ip}:{port}/play_round/{{game_id}}/{{bot_id}} with JSON body {{\"move\": \"<Rock/Paper/Scissors>\"}}")
    print("\n")
    app.run(debug=True, host='0.0.0.0', port=port)
