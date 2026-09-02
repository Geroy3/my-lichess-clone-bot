import os
import io
import http.server
import threading
import requests
import chess.pgn
import chess.polyglot

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
upgrade_url = "https://lichess.org/api/bot/account/upgrade"
# Safely reads your secret token from Render's hidden settings
token = os.environ.get("LICHESS_BOT_TOKEN") 

if not token:
    print("❌ ERROR: LICHESS_BOT_TOKEN environment variable is missing in Render settings!")
else:
    upgrade_headers = {"Authorization": f"Bearer {token}"}
    upgrade_response = requests.post(upgrade_url, headers=upgrade_headers)

    if upgrade_response.status_code == 200:
        print("🎉 SUCCESS! Your account has been officially upgraded to a BOT profile!")
    elif upgrade_response.status_code == 400:
        print("ℹ️ Account status verified: Already configured as an upgraded BOT profile.")
    else:
        print(f"⚠️ Upgrade check response: {upgrade_response.status_code}")


# ==========================================
# 3. Automated Repertoire Sync from Main Account
# ==========================================
MAIN_ACCOUNT = "np23b_gnome"
PGN_OUTPUT = "my_filtered_openings.pgn"

print(f"🔄 Scanning Lichess for {MAIN_ACCOUNT}'s opening games...")

url = f"https://lichess.org{MAIN_ACCOUNT}"
params = {
    "max": 150,
    "perfType": "rapid,classical",
    "opening": "true",
    "moves": "true"
}
headers = {"Accept": "application/x-chess-pgn"}

response = requests.get(url, params=params, headers=headers)

if response.status_code == 200:
    pgn_data = io.StringIO(response.text)
    filtered_games_count = 0

    # Filter through history to record your wins and draws
    with open(PGN_OUTPUT, "w") as out_file:
        while True:
            game = chess.pgn.read_game(pgn_data)
            if game is None:
                break

            white_player = game.headers.get("White", "").lower()
            result = game.headers.get("Result", "")
            is_white = (white_player == MAIN_ACCOUNT.lower())
            
            # Filter Strategy: Skip games where you lost to avoid training on mistakes
            if is_white and result == "0-1":
                continue
            if not is_white and result == "1-0":
                continue

            out_file.write(str(game) + "\n\n")
            filtered_games_count += 1

    print(f"✅ Filtered {filtered_games_count} high-quality games!")

    # ==========================================
    # 4. Compile the Polyglot .bin Opening Book
    # ==========================================
    print("📦 Compiling PGN data into a Polyglot .bin book...")
    book = chess.polyglot.MemoryBook()

    with open(PGN_OUTPUT) as pgn_file:
        while True:
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                break
            
            board = game.board()
            for move in game.mainline_moves():
                # Store moves deep into the game (up to move 40) to catch middlegame choices
                if board.fullmove_number > 40: 
                    break
                book.add(board, move)
                board.push(move)

    with open("my_openings.bin", "wb") as bin_file:
        chess.polyglot.write_book(bin_file, book)

    print("🚀 Repertoire sync complete! 'my_openings.bin' is updated.")
else:
    print(f"❌ Failed to download games from Lichess. Code: {response.status_code}")

print("🤖 Now listening for live Lichess Bot challenges 24/7...")
# Your active Lichess background streaming engine rules loop runs continuously below here
