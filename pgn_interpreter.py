import pgn

import main


def load_pgn_file(path):
    f = open(path)
    pgn_text = f.read()
    f.close()
    games = pgn.loads(pgn_text)
    return games

def translate_pgn_move_in_position(move, board_position, additional_board_info):
    side_to_move = additional_board_info[0]
    # castling
    if 'O' in move:
        translated_move = None
        if move == 'O-O':
            if side_to_move == 'white':
                translated_move = 'e1h1'
            elif side_to_move == 'black':
                translated_move = 'e8h8'
        elif move == 'O-O-O':
            if side_to_move == 'white':
                translated_move = 'e1a1'
            elif side_to_move == 'black':
                translated_move = 'e8a8'
        return translated_move

    #clean move data
    #remove + and # -> meaning check and checkmate, not important
    if '+' in move or '#' in move:
        move = move[:-1]
    #promotion
    promote_to = ''
    if '=' in move:
        promote_to_index = move.index('=') + 1
        promote_to = move[promote_to_index]
        if side_to_move == 'black':
            promote_to = promote_to.lower()
        move = move[:-2]

    moved_to_square = move[-2] + move[-1]
    legal_moves = main.legal_moves()
    print(move, promote_to, moved_to_square)




def translate_pgn_move_chain_in_position(moves, board_position=None, additional_board_info=None):
    if board_position == None:
        board_position = main.setup_board()
    if additional_board_info == None:
        additional_board_info = main.setup_additional_board_info()
    translated_moves = []
    for move in moves:
        translated_move = translate_pgn_move_in_position(move, board_position, additional_board_info)
        translated_moves.append(translated_move)
        board_position, additional_board_info = main.execute_move(translated_move, board_position, additional_board_info)


games = load_pgn_file('pgn_database/Wei Yi.pgn')
game0 = games[0].moves
translate_pgn_move_chain_in_position(game0)