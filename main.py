import os
import io
import http.server
import threading
import requests
import chess.pgn
import chess.polyglot
import berserk

# ==========================================
# 1. Render 24/7 Free Tier Web Portal Bypass
# ==========================================
class HealthCheckHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"SGYZK9 Engine Active 24/7!")

    def log_message(self, format, *args):
        return 

def keep_alive():
    port = int(os.environ.get("PORT", 10000))
    server = http.server.HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=keep_alive, daemon=True).start()
print("🌐 Web Portal Bound! Render health checks cleared.")


# ==========================================
# 2. Extract Token and Initialize Repertoire
# ==========================================
token = os.environ.get("LICHESS_BOT_TOKEN") 
if not token:
    print("❌ ERROR: LICHESS_BOT_TOKEN missing in Render environment variables!")
    exit()

MAIN_ACCOUNT = "np23b_gnome"
PGN_OUTPUT = "my_filtered_openings.pgn"

print(f"🔄 Syncing repertoire with {MAIN_ACCOUNT}'s recent wins...")
url = f"https://lichess.org{MAIN_ACCOUNT}"
params = {"max": 100, "perfType": "rapid,classical", "opening": "true", "moves": "true"}
headers = {"Accept": "application/x-chess-pgn"}

try:
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        pgn_data = io.StringIO(response.text)
        book = chess.polyglot.MemoryBook()
        
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

        with open("my_openings.bin", "wb") as bin_file:
            chess.polyglot.write_book(bin_file, book)
        print("🚀 Repertoire openings binary book compiled successfully!")
except Exception as e:
    print(f"⚠️ Repertoire sync skipped: {e}")


# ==========================================
# 3. Official Lichess Berserk Engine Client Loop
# ==========================================
from my_clone_engine import MyCloneEngine
print("🤖 Connecting official Berserk streaming client...")

session = berserk.TokenSession(token)
client = berserk.Client(session=session)
engine = MyCloneEngine()
BOT_USERNAME = "SGYZK9"

def play_game(game_id):
    print(f"♟️ Dedicated thread spawned for game ID: {game_id}")
    am_i_white = True # Standard baseline defaults
    
    # Establish stream connection loop
    for event in client.bots.stream_game_state(game_id):
        state = {}
        
        if event.get("type") == "gameFull":
            state = event.get("state", {})
            # Determine color seat definitively from the initial game setup structure
            white_id = event.get("white", {}).get("id", "")
            if white_id:
                am_i_white = (white_id.lower() == BOT_USERNAME.lower())
        elif event.get("type") == "gameState":
            state = event
        else:
            continue

        # Extract and parse the move string cleanly
        moves_str = state.get("moves", "").strip()
        move_list = moves_str.split() if moves_str else []

        # Reconstruct current board positions up to the active move
        board = chess.Board()
        for move_uci in move_list:
            if move_uci:
                board.push_uci(move_uci)

        # Check turn logic natively (True = White, False = Black)
        is_white_turn = board.turn == chess.WHITE

        # Fixed Turn Logic Condition: Is it the bot's turn to move?
        if (is_white_turn and am_i_white) or (not is_white_turn and not am_i_white):
            print(f"⚡ SGYZK9 is calculating move for turn {board.fullmove_number}...")
            bot_move = engine.search(board)
            if bot_move:
                try:
                    client.bots.make_move(game_id, bot_move.uci())
                    print(f"🚀 Played move successfully: {bot_move.uci()}")
                except Exception as e:
                    print(f"⚠️ Move dispatch warning error: {e}")

def listen_for_events():
    print("✅ Online! SGYZK9 is listening for incoming match requests...")
    for event in client.bots.stream_incoming_events():
        if event.get("type") == "challenge":
            challenge_id = event["challenge"]["id"]
            challenger_name = event["challenge"]["challenger"]["id"]
            print(f"⚔️ Match invitation received from: {challenger_name}")
            try:
                client.bots.accept_challenge(challenge_id)
                print(f"✅ Auto-accepted challenge ID: {challenge_id}")
            except Exception as e:
                print(f"❌ Failed to intercept challenge: {e}")
                
        elif event.get("type") == "gameStart":
            game_id = event["game"]["id"]
            threading.Thread(target=play_game, args=(game_id,), daemon=True).start()

listen_for_events()
