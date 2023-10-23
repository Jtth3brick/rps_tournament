import sys
import requests
from bot import ai_rps

def play_game(ip_address, port):
    base_url = f"http://{ip_address}:{port}"
    bot = ai_rps()

    for _ in range(3000):
        # Make a move
        move = bot.play()
        response = requests.post(f"{base_url}/play_round/game_id/bot_id", json={"move": move})
        data = response.json()

        if 'opponent_move' in data:
            bot.update(data['opponent_move'])
        else:
            # Handle cases where the opponent hasn't moved or some error occurred
            print(data['status'])
            break # assume someone was disqualified and end excecution

        # Check for game ending conditions
        if 'message' in data and 'Game over' in data['message']:
            print(data['message'])
            break

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script_name.py <IP_ADDRESS> <PORT>")
        sys.exit(1)

    ip_address = sys.argv[1]
    port = sys.argv[2]

    play_game(ip_address, port)
