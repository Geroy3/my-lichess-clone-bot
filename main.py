# ==========================================
# 4. Live Lichess Challenge & Game Event Loop
# ==========================================
print("🤖 Connecting to Lichess Live Event Stream...")
engine = MyCloneEngine()

# CHANGE THIS: Tell the bot its own username so it knows when it's playing!
BOT_USERNAME = "SGYZK9"  

def handle_game_stream(game_id):
    stream_url = f"https://lichess.org{game_id}"
    game_response = requests.get(stream_url, headers=upgrade_headers, stream=True)
    
    for line in game_response.iter_lines():
        if line:
            event = json.loads(line.decode('utf-8'))
            
            # Read game state updates
            if event.get("type") in ["gameFull", "gameState"]:
                state = event.get("state", event)
                moves_str = state.get("moves", "")
                
                # Reconstruct the current board positions
                board = chess.Board()
                for move in moves_str.split():
                    if move:
                        board.push_san(move)
                
                # 1. Check whose turn it is natively (True = White, False = Black)
                is_white_turn = board.turn == chess.WHITE
                
                # 2. Extract who is playing White in this specific match
                white_player_id = event.get("white", {}).get("id", "")
                if not white_player_id and "gameFull" in event:
                    white_player_id = event["gameFull"]["white"].get("id", "")
                
                # 3. Determine if the bot is White or Black
                am_i_white = (white_player_id.lower() == BOT_USERNAME.lower())
                
                # 4. Move calculation trigger: If it matches, calculate and play!
                if (is_white_turn and am_i_white) or (not is_white_turn and not am_i_white):
                    print(f"🤔 Bot is thinking on move {board.fullmove_number}...")
                    bot_move = engine.search(board)
                    
                    if bot_move:
                        move_url = f"https://lichess.org{game_id}/move/{bot_move.uci()}"
                        move_res = requests.post(move_url, headers=upgrade_headers)
                        if move_res.status_code == 200:
                            print(f"🚀 Played move: {bot_move.uci()}")
                        else:
                            print(f"⚠️ Move submission failed: {move_res.text}")

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
