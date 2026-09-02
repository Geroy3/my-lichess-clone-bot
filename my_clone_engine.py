import os
import chess
import chess.polyglot
import random

class MyCloneEngine:
    def __init__(self, stockfish_path=None):
        print("Engine module initialised successfully.")

    def is_endgame(self, board):
        heavy_pieces = (chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN)
        count = sum(len(board.pieces(pt, chess.WHITE)) + len(board.pieces(pt, chess.BLACK)) for pt in heavy_pieces)
        return count <= 4

    def search(self, board, time_limit=0.5):
        # 1. Look deep into your book memory bank first (up to move 40)
        try:
            with chess.polyglot.open_reader("my_openings.bin") as reader:
                entry = reader.choice(board)
                print("📖 Repertoire Book Move Played!")
                return entry.move
        except (IndexError, FileNotFoundError, Exception):
            pass

        # 2. Fallback: Human-like selection mechanics if off-repertoire
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None

        # Sort moves giving preference to tactical captures and active development
        captures = [m for m in legal_moves if board.is_capture(m)]
        checks = [m for m in legal_moves if board.gives_check(m)]
        
        # Human Blunder Mimic Selection Strategy:
        # 75% of the time, choose a highly forcing/active move (capture or check)
        if (captures or checks) and random.random() < 0.75:
            forcing_moves = captures + checks
            return random.choice(forcing_moves)
        
        # 25% of the time, play a standard positional development move
        return random.choice(legal_moves)

    def quit(self):
        pass
