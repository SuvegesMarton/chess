import csv
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
    knight_position_values = [[0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9],
                              [0.9, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.9],
                              [0.9, 0.95, 1, 1, 1, 1, 0.95, 0.9],
                              [0.9, 0.95, 1, 1, 1, 1, 0.95, 0.9],
                              [0.9, 0.95, 1, 1, 1, 1, 0.95, 0.9],
                              [0.9, 0.95, 1, 1, 1, 1, 0.95, 0.9],
                              [0.9, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.9],
                              [0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9]]
    material_sum = 0
    for i in range(len(board_state)):
        for j in range(len(board_state[i])):
            if not board_state[i][j] in ['', 'k', 'K']:
                if board_state[i][j] in ['n', 'N']:
                    multiplier = knight_position_values[i][j]
                    material_sum += piece_values[board_state[i][j]] * multiplier
                else:
                    material_sum += piece_values[board_state[i][j]]
    return material_sum


def minimax(side_to_move, board_state, additional_board_info, depth, best_so_far):
    if depth == 0:
        return static_evaluation(board_state), 1
    else:
        legals = main.legal_moves(board_state, additional_board_info)
        investigated_positions = len(legals)
        if side_to_move == 'white':
            best_eval = -1000
            for move in legals:
                new_board_state, new_additional_board_info = main.execute_move(move, board_state, additional_board_info)
                position_evaluation, inv = minimax('black', new_board_state, new_additional_board_info, depth - 1, best_eval)
                investigated_positions += inv
                if best_eval < position_evaluation:
                    best_eval = position_evaluation
                if best_eval > best_so_far:
                    return best_eval, investigated_positions
            return best_eval, investigated_positions
        else:
            best_eval = 1000
            for move in legals:
                new_board_state, new_additional_board_info = main.execute_move(move, board_state, additional_board_info)
                position_evaluation, inv = minimax('white', new_board_state, new_additional_board_info, depth - 1, best_eval)
                investigated_positions += inv
                if best_eval > position_evaluation:
                    best_eval = position_evaluation
                if best_eval < best_so_far:
                    return best_eval, investigated_positions
            return best_eval, investigated_positions


def find_best_move_with_minimax(board_state, additional_board_info, depth):
    side_to_move = additional_board_info[0]
    legals = main.legal_moves(board_state, additional_board_info)
    investigated_positions = len(legals)
    if len(legals) == 0:
        return None, 1, 0
    if side_to_move == 'white':
        best_eval = -1000
        best_moves = []
        for move in legals:
            new_board_state, new_additional_board_info = main.execute_move(move, board_state, additional_board_info)
            position_evaluation, inv = minimax('black', new_board_state, new_additional_board_info, depth, best_eval)
            investigated_positions += inv
            if position_evaluation > best_eval:
                best_eval = position_evaluation
                best_moves = [move]
            elif position_evaluation == best_eval:
                best_moves.append(move)
        return choice(best_moves), investigated_positions, best_eval
    elif side_to_move == 'black':
        best_eval = 1000
        best_moves = []
        for move in legals:
            new_board_state, new_additional_board_info = main.execute_move(move, board_state, additional_board_info)
            position_evaluation, inv = minimax('white', new_board_state, new_additional_board_info, depth, best_eval)
            investigated_positions += inv
            if position_evaluation < best_eval:
                best_eval = position_evaluation
                best_moves = [move]
            elif position_evaluation == best_eval:
                best_moves.append(move)
            main.pygame.event.get()
        return choice(best_moves), investigated_positions, best_eval


class DatabaseHandler:
    def __init__(self, database_path):
        # load data from csv file
        self.database = list(csv.reader(open(database_path)))
        self.moves_played = []
        self.in_database = True

    def find_move_with_database(self, moves_played, board_state, additional_board_info, depth, display_infos):
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
            move, investigated_positions, best_eval = find_best_move_with_minimax(board_state, additional_board_info, depth)[0]
            print("number of investigated positions:", investigated_positions)
            print('dynamic eval:', best_eval)
            return move



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

