import requests
import sys

def start_game(num_rounds, ip_address="127.0.0.1", port=5001):
    url = f"http://{ip_address}:{port}/start_game"
    response = requests.post(url, json={"num_rounds": num_rounds})
    if response.status_code == 200:
        data = response.json()
        print(data["message"])
        print(f"Game ID: {data['game_id']}")
        print(f"Bot 1 ID: {data['bot1_id']}")
        print(f"Bot 2 ID: {data['bot2_id']}")
    else:
        print("Error starting the game:", response.content.decode())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python startGame.py <number_of_rounds> [ip_address] [port]")
        sys.exit(1)

    num_rounds = int(sys.argv[1])
    ip_address = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 5001

    start_game(num_rounds, ip_address, port)
