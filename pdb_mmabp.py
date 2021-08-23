import csv
import ast
import numpy as np

import minimax_abp
import main

database = None
database_path = './position_database.csv'

def is_same_FEN(fen1, fen2, board_state_match=True, sides_to_move_match=True, castling_abilities_match=False, en_passant_targets_match=False, halfmove_clock_match=False, move_number_match=False):
    fen1chunks = fen1.split(' ')
    fen2chunks = fen2.split(' ')
    if board_state_match:
        if fen1chunks[0] != fen2chunks[0]:
            return False
    if sides_to_move_match:
        if fen1chunks[1] != fen2chunks[1]:
            return False
    if castling_abilities_match:
        if fen1chunks[2] != fen2chunks[2]:
            return False
    if en_passant_targets_match:
        if fen1chunks[0] != fen2chunks[0]:
            return False
    if halfmove_clock_match:
        if fen1chunks[0] != fen2chunks[0]:
            return False
    if move_number_match:
        if fen1chunks[0] != fen2chunks[0]:
            return False
    return True


def fen_in_database(database, fen):
    for index in range(len(database)):
        if is_same_FEN(database[index][0], fen):
            return index
    return False


def load_database():
    global database
    database = list(csv.reader(open(database_path)))


def find_best_move(board_position, additional_board_info):
    if additional_board_info[0] == 'white':
        minimax_depth = main.WHITE_DEPTH
    elif additional_board_info[0] == 'black':
        minimax_depth = main.BLACK_DEPTH
    fen = main.FEN_by_setup(board_position, additional_board_info)
    index = fen_in_database(database, fen)
    legal_moves = main.legal_moves(board_position, additional_board_info)
    if index is not False:
        fen_line = database[index]
        moves = ast.literal_eval(fen_line[1])
        weights = np.asarray(ast.literal_eval(fen_line[2])).astype(np.float32)
        s = sum(weights)
        weights /= s
        move = np.random.choice(moves, 1, p=weights)
        if move in legal_moves:
            print('chosen with database size', int(s))
            return move[0]
    print('moved randomly')
    return minimax_abp.find_best_move(board_position, additional_board_info)[0]