import csv
import main
from random import choice

database = []
in_database = True
database_path = './csv_database.csv'


def find_random_move(board_state, additional_board_info):
    legals = main.legal_moves(board_state, additional_board_info)
    if len(legals) == 0:
        return None
    else:
        return choice(legals)

def load_database():
    global database
    database = list(csv.reader(open(database_path)))

def find_move_with_database(board_state, additional_board_info):
    moves_played = main.moves_played
    print(moves_played)
    if additional_board_info[0] == 'white':
        display_info = main.WHITE_VERBOSE
    elif additional_board_info[0] == 'black':
        display_info = main.BLACK_VERBOSE
    global database
    global in_database
    relevant_games = []
    if in_database:
        for game in database:
            if game[:len(moves_played)] == moves_played and len(game) > len(moves_played):
                relevant_games.append(game)

    if len(relevant_games) > 0:
        database = relevant_games
        if display_info:
            display_database(len(moves_played))
            print('Size of database at this position:', len(relevant_games))
        return choice(relevant_games)[len(moves_played)]
    else:
        if display_info:
            print('Out of database.')
        in_database = False
        return choice(main.legal_moves(board_state, additional_board_info))



def display_database(depth):
    if in_database:
        moves = []
        occurence = []
        for i in database:
            if len(i) > depth:
                new_move = i[depth]
                if new_move in moves:
                    occurence[moves.index(new_move)] += 1
                else:
                    moves.append(new_move)
                    occurence.append(1)
        print(moves)
        print(occurence)
    else:
        print('Out of database.')
