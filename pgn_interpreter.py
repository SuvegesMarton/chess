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
    # clean move data
    # remove + and # -> meaning check and checkmate, not important
    if '+' in move or '#' in move:
        move = move[:-1]
    # promotion
    promote_to = ''
    if '=' in move:
        promote_to_index = move.index('=') + 1
        promote_to = move[promote_to_index]
        if side_to_move == 'black':
            promote_to = promote_to.lower()
        move = move[:-2]

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

    moved_to_square = move[-2:]
    other_parts = move[:-2]
    legal_moves = main.legal_moves(board_position, additional_board_info)
    candidate_moves = []
    for legal in legal_moves:
        if moved_to_square == legal[2:4]:
            candidate_moves.append(legal)
    if len(candidate_moves) == 1:
        return candidate_moves[0] + promote_to
    else:
        #clean other parts, x = captures, not important
        if 'x' in other_parts:
            other_parts = other_parts[:-1]

        for i in other_parts:
            remaining_candidates = []
            if i.isupper():#i means the moving piece's name
                for j in candidate_moves:
                    moving_piece = main.find_square_by_letter_address(j[:2], board_position)
                    if moving_piece == i or moving_piece == i.lower():
                        remaining_candidates.append(j)
            elif i.islower():#i means the file where the piece has moved from
                for j in candidate_moves:
                    if i == j[0]:
                        remaining_candidates.append(j)
            elif i.isdigit():#i means the rank where the piece has moved from
                for j in candidate_moves:
                    if i == j[1]:
                        remaining_candidates.append(j)

            candidate_moves = remaining_candidates

        if len(candidate_moves) == 1:
            return candidate_moves[0] + promote_to
        else:
            for candidate in candidate_moves:
                if main.find_square_by_letter_address(candidate[:2], board_position) in ['p', 'P']:
                    return candidate


def translate_pgn_move_chain_in_position(moves, board_position=None, additional_board_info=None):
    if board_position == None:
        board_position = main.setup_board()
    if additional_board_info == None:
        additional_board_info = main.setup_additional_board_info()
    translated_moves = []
    if '-' in moves[-1] or '*' in moves[-1]:#if the last element is the result of the game
        moves = moves[:-1]
    for move in moves:
        if '{' in moves or '(' in moves or '$' in moves:#annotated game
            return None
        translated_move = translate_pgn_move_in_position(move, board_position, additional_board_info)
        translated_moves.append(translated_move)
        board_position, additional_board_info = main.execute_move(translated_move, board_position, additional_board_info)
    return translated_moves


def translate_one_file_of_games(path):
    #file must be a pgn file
    games = load_pgn_file(path)
    counter = 0
    for game in games:
        print(counter)
        print(game.moves)
        translated = translate_pgn_move_chain_in_position(game.moves)
        if translated != None:
            print(translated)
        else:
            print('ugly annotated game detected')
        counter += 1
if __name__ == "__main__":
    translate_one_file_of_games('pgn_database/Wei Yi.pgn')


