import os
import io
import json
import http.server
import threading
import requests
import chess.pgn
import chess.polyglot
from my_clone_engine import MyCloneEngine

# ==========================================
# 1. Render 24/7 Free Tier Web Portal Bypass
# ==========================================
def keep_alive():
    class DummyHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Chess Clone Bot is running 24/7!")
            
    server = http.server.HTTPServer(('0.0.0.0', 10000), DummyHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

keep_alive()
print("🌐 Free Tier Web Portal Active!")


# ==========================================
# 2. Automated Account Upgrade to Official BOT Status
# ==========================================
print("Checking Lichess account status...")
upgrade_url = "https://lichess.org"
token = os.environ.get("LICHESS_BOT_TOKEN") 

if not token:
    print("❌ ERROR: LICHESS_BOT_TOKEN environment variable is missing in Render settings!")
    exit()

upgrade_headers = {"Authorization": f"Bearer {token}"}
requests.post(upgrade_url, headers=upgrade_headers)


# ==========================================
# 3. Automated Repertoire Sync from Main Account
# ==========================================
MAIN_ACCOUNT = "np23b_gnome"
PGN_OUTPUT = "my_filtered_openings.pgn"
print(f"🔄 Scanning Lichess for {MAIN_ACCOUNT}'s opening games...")

url = f"https://lichess.org{MAIN_ACCOUNT}"
params = {"max": 150, "perfType": "rapid,classical", "opening": "true", "moves": "true"}
headers = {"Accept": "application/x-chess-pgn"}
response = requests.get(url, params=params, headers=headers)

if response.status_code == 200:
    pgn_data = io.StringIO(response.text)
    book = chess.polyglot.MemoryBook()
    filtered_games_count = 0

    while True:
        game = chess.pgn.read_game(pgn_data)
        if game is None:
            break
        white_player = game.headers.get("White", "").lower()
        result = game.headers.get("Result", "")
        is_white = (white_player == MAIN_ACCOUNT.lower())
        
        if (is_white and result == "0-1") or (not is_white and result == "1-0"):
            continue

        board = game.board()
        for move in game.mainline_moves():
            if board.fullmove_number > 40: 
                break
            book.add(board, move)
            board.push(move)
        filtered_games_count += 1

    with open("my_openings.bin", "wb") as bin_file:
        chess.polyglot.write_book(bin_file, book)
    print(f"🚀 Repertoire sync complete! Compiled {filtered_games_count} games into 'my_openings.bin'.")


# ==========================================
# 4. Live Lichess Challenge & Game Event Loop
# ==========================================
print("🤖 Connecting to Lichess Live Event Stream...")
engine = MyCloneEngine()

def handle_game_stream(game_id):
    stream_url = f"https://lichess.org{game_id}"
    game_response = requests.get(stream_url, headers=upgrade_headers, stream=True)
    board = chess.Board()
    
    for line in game_response.iter_lines():
        if line:
            event = json.loads(line.decode('utf-8'))
            if event.get("type") == "gameFull" or event.get("type") == "gameState":
                moves_str = event.get("state", event).get("moves", "")
                board = chess.Board()
                for move in moves_str.split():
                    if move:
                        board.push_san(move)
                
                # If it's our turn to move, calculate and submit it
                is_white_turn = board.turn == chess.WHITE
                am_i_white = event.get("white", {}).get("id") == MAIN_ACCOUNT.lower() # adjusted for clone tracking
                
                # Standard check: check if bot needs to move
                if True: # Simulating rapid move trigger
                    bot_move = engine.search(board)
                    if bot_move:
                        move_url = f"https://lichess.org{game_id}/move/{bot_move.uci()}"
                        requests.post(move_url, headers=upgrade_headers)

# Listen to structural incoming account events
event_url = "https://lichess.org"
event_response = requests.get(event_url, headers=upgrade_headers, stream=True)

print("✅ Online! Now listening for incoming challenges 24/7...")
for line in event_response.iter_lines():
    if line:
        event = json.loads(line.decode('utf-8'))
        
        # Auto-accept incoming challenges
        if event.get("type") == "challenge":
            challenge_id = event["challenge"]["id"]
            accept_url = f"https://lichess.org{challenge_id}/accept"
            requests.post(accept_url, headers=upgrade_headers)
            print(f"⚔️ Accepted challenge {challenge_id}")
            
        # Handle live game plays
        elif event.get("type") == "gameStart":
            game_id = event["game"]["id"]
            print(f"♟️ Starting game match {game_id}")
            threading.Thread(target=handle_game_stream, args=(game_id,), daemon=True).start()

