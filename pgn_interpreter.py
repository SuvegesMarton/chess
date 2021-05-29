import pgn
import os
import csv

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
    while move[-1] in ['+', '#', '!', '?']:
        move = move[:-1]
    # promotion
    promote_to = ''
    if '=' in move:
        promote_to_index = move.index('=') + 1
        promote_to = move[promote_to_index]
        if side_to_move == 'black':
            promote_to = promote_to.lower()
        move = move[:-2]
    #print('pt:', promote_to)

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
    #print(legal_moves)
    candidate_moves = []
    for legal in legal_moves:
        if moved_to_square == legal[2:4]:
            candidate_moves.append(legal)
    if len(candidate_moves) == 1:
        return candidate_moves[0] + promote_to
    else:
        # clean other parts, x = captures, not important
        if 'x' in other_parts:
            other_parts = other_parts[:-1]

        for i in other_parts:
            remaining_candidates = []
            if i.isupper():  # i means the moving piece's name
                for j in candidate_moves:
                    moving_piece = main.find_square_by_letter_address(j[:2], board_position)
                    if moving_piece == i or moving_piece == i.lower():
                        remaining_candidates.append(j)
            elif i.islower():  # i means the file where the piece has moved from
                for j in candidate_moves:
                    if i == j[0]:
                        remaining_candidates.append(j)
            elif i.isdigit():  # i means the rank where the piece has moved from
                for j in candidate_moves:
                    if i == j[1]:
                        remaining_candidates.append(j)

            candidate_moves = remaining_candidates

        if len(candidate_moves) == 1:
            return candidate_moves[0] + promote_to
        else:
            for candidate in candidate_moves:
                if main.find_square_by_letter_address(candidate[:2], board_position) in ['p', 'P']:
                    if len(candidate) == 4:
                        return candidate
                    else:
                        return candidate[:4] + promote_to


def translate_pgn_move_chain_in_position(moves, board_position=None, additional_board_info=None):
    if board_position is None:
        board_position = main.setup_board()
    if additional_board_info is None:
        additional_board_info = main.setup_additional_board_info()
    translated_moves = []
    while True:
        if '-' in moves[-1] or '*' in moves[-1]:  # if the last element/elements are the result of the game
            moves = moves[:-1]
        else:
            break
    for move in moves:
        if '{' in move or '(' in move or '$' in move or '!' in move:  # annotated game
            return None
        translated_move = translate_pgn_move_in_position(move, board_position, additional_board_info)
        #print(move, translated_move, board_position, additional_board_info)
        translated_moves.append(translated_move)
        board_position, additional_board_info = main.execute_move(translated_move, board_position, additional_board_info)
    return translated_moves


def translate_one_file_of_games(path):
    # file must be a pgn file
    games = load_pgn_file(path)
    translated_games = [None] * len(games)
    counter = 1
    for game in games:
        print('path:', path, 'game no.', counter)
        counter += 1
        print("original:", game.moves)
        if game.fen is not None: # odds game, not wtih basic setup
            print('different starting position detected:', game.fen)
            continue
        translated = translate_pgn_move_chain_in_position(game.moves)
        if translated is None:
            print('ugly annotated game detected')
            continue
        else:
            print("translated:", translated)
        translated_games[games.index(game)] = translated
    return translated_games


def save_games_to_csv(translated_games, path):
    with open(path, 'a', newline='') as file:
        writer = csv.writer(file)
        print(translated_games)
        for game in translated_games:
            if game is not None:
                writer.writerow(game)


def search_logfile(logfile_path, searched_item):
    with open(logfile_path, 'r') as logfile:
        data = logfile.read()
        if searched_item in data:
            return True
        else:
            return False


def append_logfile(logfile_path, new_item):
    with open(logfile_path, 'a') as logfile:
        logfile.write(new_item)
        logfile.write("\n")


def translate_all_pgn_to_csv_with_logging(pgns_folder_path, csv_path, logfile_path):
    pgn_file_paths = os.listdir(pgns_folder_path)

    for filepath in pgn_file_paths:

        print("Translating", filepath)
        if search_logfile(logfile_path, filepath):  # pgn file has been already translated(listed in the logfile)
            print("File", filepath, "has been already translated")
            continue
        translated_games = translate_one_file_of_games(pgns_folder_path + filepath)
        save_games_to_csv(translated_games, csv_path)
        append_logfile(logfile_path, filepath)
        print("Translated file:", filepath)


if __name__ == "__main__":
    translate_all_pgn_to_csv_with_logging('pgn_database/', 'csv_database.csv', 'csv_database_log.txt')
