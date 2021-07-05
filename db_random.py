import csv
import main
from random import choice

def find_random_move(board_state, additional_board_info):
    legals = main.legal_moves(board_state, additional_board_info)
    if len(legals) == 0:
        return None
    else:
        return choice(legals)

class DatabaseHandler:
    def __init__(self, database_path):
        # load data from csv file
        self.database = list(csv.reader(open(database_path)))
        self.moves_played = []
        self.in_database = True

    def find_move_with_database(self, moves_played, board_state, additional_board_info, display_infos):
        relevant_games = []
        if self.in_database:
            for game in self.database:
                if game[:len(moves_played)] == moves_played and len(game) > len(moves_played):
                    relevant_games.append(game)

        if len(relevant_games) > 0:
            self.database = relevant_games
            if display_infos:
                self.display_database(len(moves_played))
            print('Size of database at this position:', len(relevant_games))
            return choice(relevant_games)[len(moves_played)]
        else:
            if display_infos:
                print('Out of database.')
            self.in_database = False
            return choice(main.legal_moves(board_state, additional_board_info))



    def display_database(self, depth):
        if self.in_database:
            moves = []
            occurence = []
            for i in self.database:
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
