import pgn

def load_pgn_file(path):
    f = open(path)
    pgn_text = f.read()
    f.close()
    games = pgn.loads(pgn_text)
    return games

games = load_pgn_file('pgn_database/Wei Yi.pgn')
for game in games:
    print(game.moves)