import main
from random import choice

def static_evaluation(board_state):
    #positive-good for white, negative-good for black
    #material
    piece_values = {'R': 5,
                    'N': 3,
                    'B': 3,
                    'Q': 9,
                    'P': 1,
                    'r': -5,
                    'n': -3,
                    'b': -3,
                    'q': -9,
                    'p': -1
                    }
    material_sum = 0
    for i in board_state:
        for j in i:
            if not j in ['', 'k', 'K']:

                material_sum += piece_values[j]
    return material_sum

def minimax(side_to_move, board_state, additional_board_info, depth):
    if depth == 0:
        return static_evaluation(board_state)
    else:
        legals = main.legal_moves(side_to_move, board_state, additional_board_info)
        if side_to_move == 'white':
            best_eval = -1000
            for move in legals:
                new_board_state, new_additional_board_info = main.execute_move(move, board_state, additional_board_info)
                position_evaluation = minimax('black', new_board_state, new_additional_board_info, depth - 1)
                if best_eval < position_evaluation:
                    best_eval = position_evaluation
            return best_eval
        else:
            best_eval = 1000
            for move in legals:
                new_board_state, new_additional_board_info = main.execute_move(move, board_state, additional_board_info)
                position_evaluation = minimax('white', new_board_state, new_additional_board_info, depth - 1)
                if best_eval > position_evaluation:
                    best_eval = position_evaluation
            return best_eval

def find_best_move(board_state, additional_board_info, depth):
    side_to_move =additional_board_info[0]
    legals = main.legal_moves(side_to_move, board_state, additional_board_info)
    if len(legals) == 0:
        return None
    if side_to_move == 'white':
        best_eval = -1000
        best_moves = []
        for move in legals:
            new_board_state, new_additional_board_info = main.execute_move(move, board_state, additional_board_info)
            position_evaluation = minimax('black', new_board_state, new_additional_board_info, depth)
            if position_evaluation > best_eval:
                best_eval = position_evaluation
                best_moves = [move]
            elif position_evaluation == best_eval:
                best_moves.append(move)
        return choice(best_moves)
    elif side_to_move == 'black':
        best_eval = 1000
        best_moves = []
        for move in legals:
            new_board_state, new_additional_board_info = main.execute_move(move, board_state, additional_board_info)
            position_evaluation = minimax('white', new_board_state, new_additional_board_info, depth)
            if position_evaluation < best_eval:
                best_eval = position_evaluation
                best_moves = [move]
            elif position_evaluation == best_eval:
                best_moves.append(move)
        return choice(best_moves)