import os
import chess
import chess.engine
import random

class MyCloneEngine:
    def __init__(self, stockfish_path="stockfish"):
        # Try to locate the stockfish binary installed by stockfish-binary on Render
        # If it's not found standardly, it falls back to the default word
        server_path = os.environ.get("STOCKFISH_PATH", stockfish_path)
        self.stockfish = chess.engine.SimpleEngine.popen_uci(server_path)

    def is_endgame(self, board):
        heavy_pieces = (chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN)
        count = sum(len(board.pieces(pt, chess.WHITE)) + len(board.pieces(pt, chess.BLACK)) for pt in heavy_pieces)
        return count <= 4

    def search(self, board, time_limit=0.5):
        # 1. Check opening book memory bank
        try:
            with chess.polyglot.open_reader("my_openings.bin") as reader:
                entry = reader.choice(board)
                print("📖 Book Move Played!")
                return entry.move
        except (IndexError, FileNotFoundError):
            pass

        # 2. Fast endgame blitz timing
        if self.is_endgame(board):
            time_limit = 0.1

        # 3. Request top engine choices
        analysis = self.stockfish.analyse(board, chess.engine.Limit(time=time_limit), multipv=3)
        moves = [lineget("pv")[] for line in analysis if "pv" in line and line.get("pv")]

        if not moves:
            return random.choice(list(board.legal_moves))

        # 4. Human blunder mimic adjustments
        if random.random() < 0.75:
            return moves
        else:
            return moves if len(moves) > 1 else moves

    def quit(self):
        self.stockfish.quit()

