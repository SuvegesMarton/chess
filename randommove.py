import main
from random import choice

def choose_move(board_state, additional_board_info):
    legals = main.legal_moves(board_state, additional_board_info)
    if len(legals) == 0:
        return None
    else:
        return choice(legals)