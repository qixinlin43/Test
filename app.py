from flask import Flask, render_template, jsonify, request
from test import ChessBoard, ChessEngine, Color, Move
import copy

app = Flask(__name__)

# Store game state
games = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/new_game', methods=['POST'])
def new_game():
    data = request.json
    game_id = data.get('game_id', 'default')
    human_color = Color.WHITE if data.get('human_color') == 'white' else Color.BLACK

    board = ChessBoard()
    engine = ChessEngine(depth=3)

    games[game_id] = {
        'board': board,
        'engine': engine,
        'human_color': human_color
    }

    # If computer plays first, make a move
    computer_move = None
    if board.current_player != human_color:
        move = engine.get_best_move(board)
        if move:
            board.make_move(move)
            computer_move = {
                'from': position_to_string(*move.start_pos),
                'to': position_to_string(*move.end_pos)
            }

    return jsonify({
        'success': True,
        'board': get_board_state(board),
        'current_player': board.current_player.value,
        'computer_move': computer_move
    })

@app.route('/api/move', methods=['POST'])
def make_move():
    data = request.json
    game_id = data.get('game_id', 'default')
    from_pos = data.get('from')
    to_pos = data.get('to')

    if game_id not in games:
        return jsonify({'success': False, 'error': 'Game not found'})

    game = games[game_id]
    board = game['board']

    # Parse positions
    try:
        start_pos = parse_position(from_pos)
        end_pos = parse_position(to_pos)
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)})

    # Find and validate move
    legal_moves = board.get_all_legal_moves(board.current_player)
    player_move = None
    for move in legal_moves:
        if move.start_pos == start_pos and move.end_pos == end_pos:
            player_move = move
            break

    if not player_move:
        return jsonify({'success': False, 'error': 'Invalid move'})

    # Make player move
    board.make_move(player_move)

    # Check game over
    game_over, winner = board.is_game_over()
    if game_over:
        return jsonify({
            'success': True,
            'board': get_board_state(board),
            'current_player': board.current_player.value,
            'game_over': True,
            'winner': winner.value if winner else 'draw',
            'in_check': False
        })

    # Make computer move
    computer_move = None
    if board.current_player != game['human_color']:
        move = game['engine'].get_best_move(board)
        if move:
            board.make_move(move)
            computer_move = {
                'from': position_to_string(*move.start_pos),
                'to': position_to_string(*move.end_pos)
            }

    # Check game over again after computer move
    game_over, winner = board.is_game_over()

    return jsonify({
        'success': True,
        'board': get_board_state(board),
        'current_player': board.current_player.value,
        'computer_move': computer_move,
        'game_over': game_over,
        'winner': winner.value if winner else 'draw' if game_over else None,
        'in_check': board.is_in_check(board.current_player)
    })

@app.route('/api/legal_moves', methods=['POST'])
def get_legal_moves():
    data = request.json
    game_id = data.get('game_id', 'default')
    from_pos = data.get('from')

    if game_id not in games:
        return jsonify({'success': False, 'error': 'Game not found'})

    game = games[game_id]
    board = game['board']

    try:
        start_pos = parse_position(from_pos)
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)})

    moves = board.get_legal_moves(start_pos[0], start_pos[1])
    legal_positions = [position_to_string(*move.end_pos) for move in moves]

    return jsonify({
        'success': True,
        'legal_moves': legal_positions
    })

def get_board_state(board):
    state = []
    for row in range(8):
        row_data = []
        for col in range(8):
            piece = board.get_piece(row, col)
            if piece:
                row_data.append({
                    'type': piece.piece_type.value,
                    'color': piece.color.value,
                    'symbol': str(piece)
                })
            else:
                row_data.append(None)
        state.append(row_data)
    return state

def parse_position(pos_str):
    if len(pos_str) != 2:
        raise ValueError("Position must be in format like 'e4'")
    col = ord(pos_str[0].lower()) - ord('a')
    row = 8 - int(pos_str[1])
    if not (0 <= row < 8 and 0 <= col < 8):
        raise ValueError("Position must be valid (a1-h8)")
    return row, col

def position_to_string(row, col):
    return chr(ord('a') + col) + str(8 - row)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
