import os
import chess
import chess.polyglot
import random

class MyCloneEngine:
    def __init__(self, stockfish_path=None):
        print("Engine module fully loaded with positional fallback logic.")

    def is_endgame(self, board):
        heavy_pieces = (chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN)
        count = sum(len(board.pieces(pt, chess.WHITE)) + len(board.pieces(pt, chess.BLACK)) for pt in heavy_pieces)
        return count <= 4

    def evaluate_position(self, board):
        if board.is_checkmate():
            return -9999 if board.turn == chess.WHITE else 9999
        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        piece_values = {
            chess.PAWN: 100, 
            chess.KNIGHT: 320, 
            chess.BISHOP: 330, 
            chess.ROOK: 500, 
            chess.QUEEN: 900
        }
        score = 0
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                val = piece_values.get(piece.piece_type, 0)
                
                # Active center control bonus squares (e4, d4, e5, d5)
                if square in [chessEchessDchessEchessD]:
                    val += 30
                    
                if piece.color == chess.WHITE:
                    score += val
                else:
                    score -= val
        return score

    def search(self, board, time_limit=0.5):
        # 1. ALWAYS try your personal opening book memory bank first
        try:
            with chess.polyglot.open_reader("my_openings.bin") as reader:
                entry = reader.choice(board)
                print("📖 Repertoire Book Move Found and Played!")
                return entry.move
        except (IndexError, FileNotFoundError, Exception):
            pass

        # 2. Positional Fallback Brain (Minimax Evaluation)
        print("🧩 Off-Repertoire: Calculating best positional move...")
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None

        best_move = random.choice(legal_moves)
        best_score = -99999 if board.turn == chess.WHITE else 99999

        for move in legal_moves:
            board.push(move)
            score = self.evaluate_position(board)
            board.pop()

            if board.turn == chess.WHITE:
                if score > best_score:
                    best_score = score
                    best_move = move
            else:
                if score < best_score:
                    best_score = score
                    best_move = move

        # 3. Human Blindspot Mimic (85% play smart move, 15% shuffle variations)
        if random.random() < 0.85:
            return best_move
        else:
            return random.choice(legal_moves)

    def quit(self):
        pass
