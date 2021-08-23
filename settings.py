GAMEMODE = 0

# 0 = live game, 1 = game replay from database

BOARD_FLIPPED = False

WHITE = 1
BLACK = 7
# 0 = human player
# 1 = random moves - randommove.py
# 2 = bruteforce minimax algorithm - minimax.py
# 3 = minimax with alpha beta pruning - minimax_abp.py
# 4 = database first, then random moves - db_random.py
# 5 = database first, then minimax with alpha beta pruning - db_mmabp.py
# 6 = positional database first, then random moves - pdb_random.py
# 7 = positional database first, then minimax with alpha beta pruning - pdb_mmabp.py


WHITE_DEPTH = 2
BLACK_DEPTH = 2
# depth matters only if the player is engine

WHITE_VERBOSE = True
BLACK_VERBOSE = True
MAIN_VERBOSE = False

WITH_GUI = True
