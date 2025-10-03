import copy
import random
from enum import Enum
from typing import List, Tuple, Optional

class Color(Enum):
    WHITE = "white"
    BLACK = "black"

class PieceType(Enum):
    PAWN = "pawn"
    ROOK = "rook"
    KNIGHT = "knight"
    BISHOP = "bishop"
    QUEEN = "queen"
    KING = "king"

class Piece:
    def __init__(self, piece_type: PieceType, color: Color):
        self.piece_type = piece_type
        self.color = color
        self.has_moved = False

    def __str__(self):
        symbols = {
            (PieceType.PAWN, Color.WHITE): "♙",
            (PieceType.ROOK, Color.WHITE): "♖",
            (PieceType.KNIGHT, Color.WHITE): "♘",
            (PieceType.BISHOP, Color.WHITE): "♗",
            (PieceType.QUEEN, Color.WHITE): "♕",
            (PieceType.KING, Color.WHITE): "♔",
            (PieceType.PAWN, Color.BLACK): "♟",
            (PieceType.ROOK, Color.BLACK): "♜",
            (PieceType.KNIGHT, Color.BLACK): "♞",
            (PieceType.BISHOP, Color.BLACK): "♝",
            (PieceType.QUEEN, Color.BLACK): "♛",
            (PieceType.KING, Color.BLACK): "♚",
        }
        return symbols.get((self.piece_type, self.color), "?")

class Move:
    def __init__(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int],
                 piece: Piece, captured_piece: Optional[Piece] = None):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.piece = piece
        self.captured_piece = captured_piece
        self.is_castling = False
        self.is_en_passant = False
        self.promotion_piece = None

class ChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.current_player = Color.WHITE
        self.move_history = []
        self.en_passant_target = None
        self.setup_initial_position()

    def setup_initial_position(self):
        # Setup pawns
        for col in range(8):
            self.board[1][col] = Piece(PieceType.PAWN, Color.BLACK)
            self.board[6][col] = Piece(PieceType.PAWN, Color.WHITE)

        # Setup other pieces
        piece_order = [PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP,
                      PieceType.QUEEN, PieceType.KING, PieceType.BISHOP,
                      PieceType.KNIGHT, PieceType.ROOK]

        for col in range(8):
            self.board[0][col] = Piece(piece_order[col], Color.BLACK)
            self.board[7][col] = Piece(piece_order[col], Color.WHITE)

    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None

    def set_piece(self, row: int, col: int, piece: Optional[Piece]):
        if 0 <= row < 8 and 0 <= col < 8:
            self.board[row][col] = piece

    def is_valid_position(self, row: int, col: int) -> bool:
        return 0 <= row < 8 and 0 <= col < 8

    def display_board(self):
        print("  a b c d e f g h")
        for row in range(8):
            print(f"{8-row} ", end="")
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    print(f"{piece} ", end="")
                else:
                    print("· ", end="")
            print(f"{8-row}")
        print("  a b c d e f g h")
        print(f"Current player: {self.current_player.value}")

    def get_possible_moves(self, row: int, col: int) -> List[Move]:
        piece = self.get_piece(row, col)
        if not piece or piece.color != self.current_player:
            return []

        moves = []
        if piece.piece_type == PieceType.PAWN:
            moves = self._get_pawn_moves(row, col)
        elif piece.piece_type == PieceType.ROOK:
            moves = self._get_rook_moves(row, col)
        elif piece.piece_type == PieceType.KNIGHT:
            moves = self._get_knight_moves(row, col)
        elif piece.piece_type == PieceType.BISHOP:
            moves = self._get_bishop_moves(row, col)
        elif piece.piece_type == PieceType.QUEEN:
            moves = self._get_queen_moves(row, col)
        elif piece.piece_type == PieceType.KING:
            moves = self._get_king_moves(row, col)

        return moves

    def _get_pawn_moves(self, row: int, col: int) -> List[Move]:
        piece = self.get_piece(row, col)
        moves = []
        direction = -1 if piece.color == Color.WHITE else 1
        start_row = 6 if piece.color == Color.WHITE else 1

        # Forward move
        new_row = row + direction
        if self.is_valid_position(new_row, col) and not self.get_piece(new_row, col):
            moves.append(Move((row, col), (new_row, col), piece))

            # Double move from starting position
            if row == start_row:
                new_row = row + 2 * direction
                if self.is_valid_position(new_row, col) and not self.get_piece(new_row, col):
                    moves.append(Move((row, col), (new_row, col), piece))

        # Diagonal captures
        for dc in [-1, 1]:
            new_row, new_col = row + direction, col + dc
            if self.is_valid_position(new_row, new_col):
                target = self.get_piece(new_row, new_col)
                if target and target.color != piece.color:
                    moves.append(Move((row, col), (new_row, new_col), piece, target))

        return moves

    def _get_rook_moves(self, row: int, col: int) -> List[Move]:
        piece = self.get_piece(row, col)
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + dr * i, col + dc * i
                if not self.is_valid_position(new_row, new_col):
                    break

                target = self.get_piece(new_row, new_col)
                if target:
                    if target.color != piece.color:
                        moves.append(Move((row, col), (new_row, new_col), piece, target))
                    break
                else:
                    moves.append(Move((row, col), (new_row, new_col), piece))

        return moves

    def _get_knight_moves(self, row: int, col: int) -> List[Move]:
        piece = self.get_piece(row, col)
        moves = []
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                       (1, 2), (1, -2), (-1, 2), (-1, -2)]

        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc
            if self.is_valid_position(new_row, new_col):
                target = self.get_piece(new_row, new_col)
                if not target or target.color != piece.color:
                    moves.append(Move((row, col), (new_row, new_col), piece, target))

        return moves

    def _get_bishop_moves(self, row: int, col: int) -> List[Move]:
        piece = self.get_piece(row, col)
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + dr * i, col + dc * i
                if not self.is_valid_position(new_row, new_col):
                    break

                target = self.get_piece(new_row, new_col)
                if target:
                    if target.color != piece.color:
                        moves.append(Move((row, col), (new_row, new_col), piece, target))
                    break
                else:
                    moves.append(Move((row, col), (new_row, new_col), piece))

        return moves

    def _get_queen_moves(self, row: int, col: int) -> List[Move]:
        return self._get_rook_moves(row, col) + self._get_bishop_moves(row, col)

    def _get_king_moves(self, row: int, col: int) -> List[Move]:
        piece = self.get_piece(row, col)
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0),
                     (1, 1), (1, -1), (-1, 1), (-1, -1)]

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self.is_valid_position(new_row, new_col):
                target = self.get_piece(new_row, new_col)
                if not target or target.color != piece.color:
                    moves.append(Move((row, col), (new_row, new_col), piece, target))

        return moves

    def is_in_check(self, color: Color) -> bool:
        king_pos = self.find_king(color)
        if not king_pos:
            return False

        opponent_color = Color.BLACK if color == Color.WHITE else Color.WHITE
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.color == opponent_color:
                    moves = self.get_possible_moves(row, col)
                    for move in moves:
                        if move.end_pos == king_pos:
                            return True
        return False

    def find_king(self, color: Color) -> Optional[Tuple[int, int]]:
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.piece_type == PieceType.KING and piece.color == color:
                    return (row, col)
        return None

    def is_valid_move(self, move: Move) -> bool:
        temp_board = copy.deepcopy(self)
        temp_board.make_move(move, validate=False)
        return not temp_board.is_in_check(move.piece.color)

    def get_legal_moves(self, row: int, col: int) -> List[Move]:
        possible_moves = self.get_possible_moves(row, col)
        legal_moves = []
        for move in possible_moves:
            if self.is_valid_move(move):
                legal_moves.append(move)
        return legal_moves

    def get_all_legal_moves(self, color: Color) -> List[Move]:
        all_moves = []
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.color == color:
                    all_moves.extend(self.get_legal_moves(row, col))
        return all_moves

    def make_move(self, move: Move, validate: bool = True) -> bool:
        if validate and not self.is_valid_move(move):
            return False

        start_row, start_col = move.start_pos
        end_row, end_col = move.end_pos

        piece = self.get_piece(start_row, start_col)
        if not piece:
            return False

        # Make the move
        self.set_piece(end_row, end_col, piece)
        self.set_piece(start_row, start_col, None)
        piece.has_moved = True

        # Add to move history
        self.move_history.append(move)

        # Switch players
        self.current_player = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE

        return True

    def is_checkmate(self, color: Color) -> bool:
        if not self.is_in_check(color):
            return False
        return len(self.get_all_legal_moves(color)) == 0

    def is_stalemate(self, color: Color) -> bool:
        if self.is_in_check(color):
            return False
        return len(self.get_all_legal_moves(color)) == 0

    def is_game_over(self) -> Tuple[bool, Optional[Color]]:
        if self.is_checkmate(self.current_player):
            winner = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE
            return True, winner
        elif self.is_stalemate(self.current_player):
            return True, None
        return False, None

class ChessEngine:
    def __init__(self, depth: int = 3):
        self.depth = depth
        self.piece_values = {
            PieceType.PAWN: 100,
            PieceType.KNIGHT: 320,
            PieceType.BISHOP: 330,
            PieceType.ROOK: 500,
            PieceType.QUEEN: 900,
            PieceType.KING: 20000
        }

    def evaluate_board(self, board: ChessBoard, maximizing_color: Color) -> float:
        if board.is_checkmate(maximizing_color):
            return -999999
        if board.is_checkmate(Color.BLACK if maximizing_color == Color.WHITE else Color.WHITE):
            return 999999
        if board.is_stalemate(maximizing_color):
            return 0

        score = 0
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece:
                    piece_value = self.piece_values[piece.piece_type]
                    if piece.color == maximizing_color:
                        score += piece_value
                    else:
                        score -= piece_value

        return score

    def minimax(self, board: ChessBoard, depth: int, alpha: float, beta: float,
                maximizing: bool, maximizing_color: Color) -> float:
        if depth == 0 or board.is_game_over()[0]:
            return self.evaluate_board(board, maximizing_color)

        current_color = board.current_player
        legal_moves = board.get_all_legal_moves(current_color)

        if maximizing:
            max_eval = float('-inf')
            for move in legal_moves:
                temp_board = copy.deepcopy(board)
                temp_board.make_move(move)
                eval_score = self.minimax(temp_board, depth - 1, alpha, beta, False, maximizing_color)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in legal_moves:
                temp_board = copy.deepcopy(board)
                temp_board.make_move(move)
                eval_score = self.minimax(temp_board, depth - 1, alpha, beta, True, maximizing_color)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def get_best_move(self, board: ChessBoard) -> Optional[Move]:
        legal_moves = board.get_all_legal_moves(board.current_player)
        if not legal_moves:
            return None

        best_move = None
        best_eval = float('-inf')
        maximizing_color = board.current_player

        for move in legal_moves:
            temp_board = copy.deepcopy(board)
            temp_board.make_move(move)
            eval_score = self.minimax(temp_board, self.depth - 1, float('-inf'), float('inf'),
                                    False, maximizing_color)

            if eval_score > best_eval:
                best_eval = eval_score
                best_move = move

        return best_move

class ChessGame:
    def __init__(self, human_color: Color = Color.WHITE):
        self.board = ChessBoard()
        self.engine = ChessEngine()
        self.human_color = human_color

    def parse_position(self, pos_str: str) -> Tuple[int, int]:
        if len(pos_str) != 2:
            raise ValueError("Position must be in format like 'e4'")

        col = ord(pos_str[0].lower()) - ord('a')
        row = 8 - int(pos_str[1])

        if not (0 <= row < 8 and 0 <= col < 8):
            raise ValueError("Position must be valid (a1-h8)")

        return row, col

    def position_to_string(self, row: int, col: int) -> str:
        return chr(ord('a') + col) + str(8 - row)

    def get_human_move(self) -> Optional[Move]:
        legal_moves = self.board.get_all_legal_moves(self.board.current_player)

        if not legal_moves:
            return None

        while True:
            try:
                print("\nEnter your move (e.g., 'e2 e4') or 'quit' to exit:")
                user_input = input("> ").strip()

                if user_input.lower() == 'quit':
                    return None

                parts = user_input.split()
                if len(parts) != 2:
                    print("Please enter move in format: start_position end_position (e.g., 'e2 e4')")
                    continue

                start_pos = self.parse_position(parts[0])
                end_pos = self.parse_position(parts[1])

                # Find matching legal move
                for move in legal_moves:
                    if move.start_pos == start_pos and move.end_pos == end_pos:
                        return move

                print("Invalid move! Try again.")
                print("Legal moves from that position:", end=" ")
                piece = self.board.get_piece(start_pos[0], start_pos[1])
                if piece and piece.color == self.board.current_player:
                    piece_moves = self.board.get_legal_moves(start_pos[0], start_pos[1])
                    for move in piece_moves:
                        print(f"{self.position_to_string(*move.start_pos)}{self.position_to_string(*move.end_pos)}", end=" ")
                print()

            except ValueError as e:
                print(f"Error: {e}")
            except (KeyboardInterrupt, EOFError):
                return None

    def play(self):
        print("Welcome to Chess!")
        print(f"You are playing as {self.human_color.value}")
        print("Enter moves in format: start_position end_position (e.g., 'e2 e4')")
        print("Type 'quit' to exit the game\n")

        while True:
            self.board.display_board()

            game_over, winner = self.board.is_game_over()
            if game_over:
                if winner:
                    print(f"\nGame Over! {winner.value.title()} wins!")
                else:
                    print("\nGame Over! It's a draw!")
                break

            if self.board.is_in_check(self.board.current_player):
                print(f"{self.board.current_player.value.title()} is in check!")

            if self.board.current_player == self.human_color:
                print(f"\nYour turn ({self.human_color.value}):")
                move = self.get_human_move()
                if not move:
                    print("Thanks for playing!")
                    break

                self.board.make_move(move)
                print(f"You played: {self.position_to_string(*move.start_pos)}{self.position_to_string(*move.end_pos)}")

            else:
                print(f"\nComputer is thinking...")
                move = self.engine.get_best_move(self.board)
                if not move:
                    print("Computer has no legal moves!")
                    break

                self.board.make_move(move)
                print(f"Computer played: {self.position_to_string(*move.start_pos)}{self.position_to_string(*move.end_pos)}")

def main():
    print("Choose your color:")
    print("1. White (you go first)")
    print("2. Black (computer goes first)")

    while True:
        try:
            choice = input("Enter 1 or 2: ").strip()
            if choice == "1":
                human_color = Color.WHITE
                break
            elif choice == "2":
                human_color = Color.BLACK
                break
            else:
                print("Please enter 1 or 2")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            return

    game = ChessGame(human_color)
    game.play()

if __name__ == "__main__":
    main()