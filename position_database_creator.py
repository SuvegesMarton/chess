import csv
import main

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


def load_games(database_path):
    return list(csv.reader(open(database_path)))


def extract_data_from_game(game):
    db = []
    fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    board_position, additional_board_info = main.setup_by_FEN(fen)
    if DEPTH > len(game):
        depth = len(game)
    else:
        depth = DEPTH
    for move in game[:depth]:#does not add the full game to the database
        db.append([fen, move])
        #next move
        board_position, additional_board_info = main.execute_move(move, board_position, additional_board_info)
        fen = main.FEN_by_setup(board_position, additional_board_info)
    return db


def extract_data_from_database(database):
    extracted = []
    for game in database:
        new = extract_data_from_game(game)
        extracted += new
    return extracted


def fen_in_database(database, fen):
    for index in range(len(database)):
        if is_same_FEN(database[index][0], fen):
            return index
    return False


def add_fen_line_to_database_line(db_line, fen_line):
    move_to_add = fen_line[1]
    if move_to_add in db_line[1]:
        db_line[2][db_line[1].index(move_to_add)] += 1
    else:
        db_line[1].append(move_to_add)
        db_line[2].append(1)
    return db_line



def compress_extracted_database(database):
    compressed = []
    #lines in compressed database: [FEN code of position, [played moves from this position], [weights of moves]]
    for fen_line in database:
        index = fen_in_database(compressed, fen_line[0])
        if index is False:
            compressed.append([fen_line[0], [fen_line[1]], [1]])
        else:
            compressed[index] = add_fen_line_to_database_line(compressed[index], fen_line)
    return compressed


def write_data_to_csv(database, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file)
        for game in database:
            writer.writerow(game)


#max depth of created database
DEPTH = 3
db = load_games('csv_database.csv')
print('database loaded')
data = extract_data_from_database(db)
print('data extracted')
compressed_data = compress_extracted_database(data)
print('data compressed')
write_data_to_csv(compressed_data, 'position_database.csv')
print('data saved')

