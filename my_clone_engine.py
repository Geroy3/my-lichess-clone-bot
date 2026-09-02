import chess
import chess.engine
import random

class MyCloneEngine:
    def __init__(self, stockfish_path="stockfish"):
        # Connects to the local Stockfish binary on the server
        self.stockfish = chess.engine.SimpleEngine.popen_uci(stockfish_path)

    def is_endgame(self, board):
        # Detects if the board has transitioned to an endgame (2 or fewer heavy pieces left)
        heavy_pieces = (chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN)
        count = sum(len(board.pieces(pt, chess.WHITE)) + len(board.pieces(pt, chess.BLACK)) for pt in heavy_pieces)
        return count <= 4

    def search(self, board, time_limit=0.5):
        # 1. Look for openings/middlegames deep inside your book first
        try:
            with chess.polyglot.open_reader("my_openings.bin") as reader:
                entry = reader.choice(board)
                print("📖 Book Move Played!")
                return entry.move
        except IndexError:
            pass # Off-repertoire, let the custom engine decide

        # 2. Adjust time management for fast endgames
        if self.is_endgame(board):
            time_limit = 0.1 # Move rapidly in simple endgames, just like a human blitzing moves

        # 3. Ask Stockfish for the top 3 best moves
        analysis = self.stockfish.analyse(board, chess.engine.Limit(time=time_limit), multipv=3)
        moves = [lineget("pv")[] for line in analysis if "pv" in line]

        if not moves:
            return random.choice(list(board.legal_moves))

        # 4. Human Blunder Mimic:
        # 75% of the time, pick the absolute best engine move.
        # 25% of the time, choose the 2nd or 3rd line to simulate human tactical blind spots.
        if random.random() < 0.75:
            return moves
        else:
            return moves if len(moves) > 1 else moves

    def quit(self):
        self.stockfish.quit()
