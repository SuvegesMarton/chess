import csv
import main
import random


class DatabaseHandler:
    def __init__(self, database_path):
        # load data from csv file
        self.database = list(csv.reader(open(database_path)))
        self.moves_played = []
        self.in_database = True


    def shrink_database(self, db, new_move, move_id):
        db_size = len(db)
        new_db = [None] * db_size
        counter = 0
        for i in range(db_size):
            if len(db[i]) > move_id:
                if db[i][move_id] == new_move:
                    new_db[counter] = db[i]
                    counter += 1
        return new_db[:counter]

    def find_move(self, moves_played, board_state, additional_board_info):
        if self.in_database:
            db_before = len(self.database)
            # compare up own played moves with input played moves.
            # if they match continue with shrinking the database, otherways start over
            match = True
            for i in range(len(self.moves_played)):
                if not self.moves_played[i] == moves_played[i]:
                    match = False
                    break
            if match:
                length_difference = len(moves_played) - len(self.moves_played)
                new_moves = moves_played[-length_difference:]
                for i in range(len(new_moves)):
                    self.database = self.shrink_database(self.database, new_moves[i], len(self.moves_played) + i)
                if len(self.database) == 0:
                    self.in_database = False
                    return random.choice(main.legal_moves(board_state, additional_board_info)), db_before, 0
                chosen_game = random.choice(self.database)
                if len(chosen_game) > len(moves_played):
                    return chosen_game[len(moves_played)], db_before, len(self.database)
                else:
                    return random.choice(main.legal_moves(board_state, additional_board_info)), db_before, 0

            else:
                print('no match')
        else:
            legals = main.legal_moves(board_state, additional_board_info)
            if len(legals) == 0:
                return None, 0, 0
            else:
                return random.choice(legals), 0, 0
