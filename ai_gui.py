import pygame
import numpy as np
import cv2
from random import randint, choice
#F0D9B5; - 240, 217, 181
#946f51; - 148, 111, 81



knight_directions = [[2, 1], [2, -1], [1, 2], [1, -2], [-2, 1], [-2, -1], [-1, 2], [-1, -2]]
bishop_directions = [[1, 1], [-1, -1], [1, -1], [-1, 1]]
rook_directions = [[0, 1], [0, -1], [-1, 0], [1, 0]]
#  'colour + _ + piece name + L + start line'
white_pieces = ['white_pawnLA', 'white_pawnLB', 'white_pawnLC', 'white_pawnLD', 'white_pawnLE', 'white_pawnLF', 'white_pawnLG', 'white_pawnLH',
                'white_rookLA', 'white_knightLB', 'white_bishopLC', 'white_queen', 'white_king', 'white_bishopLF', 'white_knightLG', 'white_rookLH',]
white_alive = [1] * 16

black_pieces = ['black_rookLA', 'black_knightLB', 'black_bishopLC', 'black_queen', 'black_king', 'black_bishopLF', 'black_knightLG', 'black_rookLH',
                'black_pawnLA', 'black_pawnLB', 'black_pawnLC', 'black_pawnLD', 'black_pawnLE', 'black_pawnLF', 'black_pawnLG', 'black_pawnLH']
black_alive = [1] * 16

board_state = []
board_state += ([black_pieces[:8]])
board_state += ([black_pieces[8:]])
board_state += (['empty'] * 8,['empty'] * 8,['empty'] * 8,['empty'] * 8)
board_state += ([white_pieces[:8]])
board_state += ([white_pieces[8:]])

previous_move = None
white_rooks_moved = False
black_rooks_moved = False

with_gui = True
if with_gui:
    square_size = 100
    pygame.init()
    gameDisplay = pygame.display.set_mode((square_size*8, square_size*8))
    pygame.display.set_caption('Chess')
    clock = pygame.time.Clock()


def get_move_from_gui(color, board_state):
    legals = legal_moves(color, board_state)
    move_half_done = False
    first_half = 0
    while True:
        ev = pygame.event.get()
        for event in ev:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                line, file = pos[1] // square_size, pos[0] // square_size
                clicked_square = board_state[line][file]
                if move_half_done == True:
                    assembled_move = first_half + num_adress_to_letter((line, file))
                    if assembled_move in legals:
                        return assembled_move
                    elif 'white' in clicked_square:
                        first_half = num_adress_to_letter((line, file))
                        display_with_gui(board_state, selected_piece=clicked_square, legal_moves=legals)
                    else:
                        move_half_done = False

                elif 'white' in clicked_square:
                    first_half = num_adress_to_letter((line, file))
                    move_half_done = True
                    display_with_gui(board_state, selected_piece=clicked_square, legal_moves=legals)


def create_square_animation_map(moving_piece, board_state, legal_moves):
    #0 nothing
    #1 corners
    #2 green circle
    #3 check
    square_num = find_square_by_piece(moving_piece, board_state)
    square_letter = num_adress_to_letter(square_num)
    moves_to_animate = []
    for move in legal_moves:
        if move[:2] == square_letter:
            moves_to_animate.append(move)

    map = [[0 for i in range(8)] for i in range(8)]

    for i in moves_to_animate:
        if find_square_by_letter_adress(i[2:], board_state) != 'empty':
            num_adress = letter_adress_to_num(i[2:])
            map[num_adress[0]][num_adress[1]] = 1
        else:
            num_adress = letter_adress_to_num(i[2:])
            map[num_adress[0]][num_adress[1]] = 2
    return map

def apply_animation(img, animation_code):
    animation_code = int(animation_code)
    white = np.asarray([255, 255, 255])
    if animation_code == 0:
        return img
    elif animation_code == 1:
        squares_filter = cv2.imread('GUI/corners.png')
        for i in range(len(squares_filter)):
            for j in range(len(squares_filter[i])):
                print(np.array_equal(squares_filter[i][j], white))
                if not np.array_equal(squares_filter[i][j], white):
                    img[i][j] = squares_filter[i][j]
        return img
    elif animation_code == 2:
        circle_filter = cv2.imread('GUI/middle_circle.png')
        for i in range(len(circle_filter)):
            for j in range(len(circle_filter[i])):
                if not np.array_equal(circle_filter[i][j], white):
                    img[i][j] = circle_filter[i][j]
        return img
    else:
        return img

def load_img(img_name):
    location = 'GUI/' + img_name + '.png'
    img = pygame.image.load(location)
    img = pygame.transform.scale(img, (square_size, square_size))
    return img

def create_img(img_name):
    bg_color = [255,0,0]
    if img_name[2] == '0':
        bg_color = np.asarray([81, 111, 148])
    elif img_name[2] == '1':
        bg_color = np.asarray([181, 217, 240])
    #figures3.png; multiply by 200!
    figure_topleft_corners = {
        '1k': [0, 0],
        '1q': [0, 1],
        '1b': [0, 2],
        '1n': [0, 3],
        '1r': [0, 4],
        '1p': [0, 5],
        '0k': [1, 0],
        '0q': [1, 1],
        '0b': [1, 2],
        '0n': [1, 3],
        '0r': [1, 4],
        '0p': [1, 5],
    }
    if 'ee' in img_name:
        figure_image = np.asarray([[bg_color] * 200] * 200)

    else:
        figure_coords = figure_topleft_corners[img_name[:2]]
        figure_image = cv2.imread('GUI/figures3.png', cv2.IMREAD_COLOR)
        x, y, w, h = figure_coords[1]*200, figure_coords[0]*200, 200, 200
        figure_image = figure_image[y:y + h, x:x + w]

        white = np.asarray([255, 255, 255])
        black = np.asarray([0, 0, 0])

        for i in range(len(figure_image)):
            for j in range(len(figure_image[i])):
                if not(np.array_equal(figure_image[i][j], white)) and not(np.array_equal(figure_image[i][j], black)):
                    figure_image[i][j] = bg_color
    image = apply_animation(figure_image, img_name[-1])

    cv2.imwrite('GUI/' + img_name + '.png', image)

def get_image(img_name):
    try:
        img = load_img(img_name)
    except:
        create_img(img_name)
        img = load_img(img_name)
    return img

def img_format_name_from_square(square):
    if 'white' in square:
        c = '1'
    elif 'black' in square:
        c = '0'
    else:
        c = 'e'
    if 'pawn' in square:
        p = 'p'
    elif 'rook' in square:
        p = 'r'
    elif 'knight' in square:
        p = 'n'
    elif 'bishop' in square:
        p = 'b'
    elif 'queen' in square:
        p = 'q'
    elif 'king' in square:
        p = 'k'
    else:
        p = 'e'
    return c + p

def display_board(board):
    for row in board:
        for square in row:
            print(square + ', ', end='')
        print('')

def display_with_gui(board, selected_piece=None, legal_moves=None):
    y = 0
    start_color = 1   #even = dark, odd = light
    if selected_piece != None:
        square_animation_map = create_square_animation_map(selected_piece, board, legal_moves)
    else:
        square_animation_map = [[0 for i in range(8)] for i in range(8)]
    for i, row in enumerate(board):
        x = 0
        square_color = start_color
        for j, square in enumerate(row):
            img_name = img_format_name_from_square(square) + str(square_color%2) + str(square_animation_map[i][j])
            img = get_image(img_name)
            gameDisplay.blit(img, (x, y))
            x += square_size
            square_color += 1
        start_color += 1
        y += square_size
    pygame.display.update()

def num_adress_to_letter( adress):
    #input: 0-7
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    num = 8 - adress[0]
    lett = letters[adress[1]]
    return str(str(lett) + str(num))

def letter_adress_to_num( adress):
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    column = letters.index(adress[0])
    row = 8 - int(adress[1])
    return row, column

def find_square_by_letter_adress(adress, board_state):
    letter = adress[0].lower()
    num = 8 - int(adress[1])
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    letter_num = letters.index(letter)
    return board_state[num][letter_num]

def find_square_by_piece(piece, board_state):
    for i, row in enumerate(board_state):
        if piece in row:
            return [i, row.index(piece)]
    return None

def find_square_by_number_adress(adressY, adressX, board_state):
    return board_state[adressY][adressX]

def legal_moves_all_direction_pieces(directions, range, piece, board_state):
    if 'white' in piece:
        moving_color = 'white'
        other = 'black'
    else:
        moving_color = 'black'
        other = 'white'
    legals = []
    piece_position = find_square_by_piece(piece, board_state)
    for direction in directions:
        range_counter = 0
        position = piece_position
        while range_counter < range:
            range_counter += 1
            new_position = [position[0] + direction[0], position[1] + direction[1]]
            if 0 > new_position[0] or new_position[0] > 7 or 0 > new_position[1] or new_position[1] > 7:
                break
            square = find_square_by_number_adress(new_position[0], new_position[1], board_state)
            if square == 'empty':
                legals.append(num_adress_to_letter(piece_position) + num_adress_to_letter(new_position))
                position = new_position
            elif other in square:
                legals.append(num_adress_to_letter(piece_position) + num_adress_to_letter(new_position))
                break
            elif moving_color in square:
                break
    return legals

def execute_move(move, board_state):
    from_square = letter_adress_to_num(move[:2])
    to = letter_adress_to_num(move[2:])
    moving_piece = board_state[from_square[0]][from_square[1]]
    board_state[from_square[0]][from_square[1]] = 'empty'
    #captured = board_state[to[0]][to[1]]
    board_state[to[0]][to[1]] = moving_piece
    return board_state

def legal_moves(color, board_state, check_matters=True):
    moving_pieces = []
    if color == 'white':
        moving_pieces = white_pieces
    if color == 'black':
        moving_pieces = black_pieces
    legal = []
    #find moves
    for piece in moving_pieces:
        position = find_square_by_piece(piece, board_state)
        if position == None:
            continue
        if 'pawn' in piece:
            #double move from starting position
            if color == 'black' and position[0] == 1 and find_square_by_number_adress(3, position[1], board_state) == 'empty':
                legal.append(num_adress_to_letter(position) + num_adress_to_letter([3, position[1]]))
            if color == 'white' and position[0] == 6 and find_square_by_number_adress(4, position[1], board_state) == 'empty':
                legal.append(num_adress_to_letter(position) + num_adress_to_letter([4, position[1]]))
            #forward move
            if color == 'black' and find_square_by_number_adress(position[0] + 1, position[1], board_state) == 'empty':
                legal.append(num_adress_to_letter(position) + num_adress_to_letter([position[0] + 1, position[1]]))
            if color == 'white' and find_square_by_number_adress(position[0] - 1, position[1], board_state) == 'empty':
                legal.append(num_adress_to_letter(position) + num_adress_to_letter([position[0] - 1, position[1]]))
            #capture
            if 0 <= position[1] - 1 <= 7:
                if color == 'black' and 'white' in find_square_by_number_adress(position[0] + 1, position[1] - 1, board_state):
                    legal.append(num_adress_to_letter(position) + num_adress_to_letter([position[0] + 1, position[1] - 1]))
            if 0 <= position[1] + 1 <= 7:
                if color == 'black' and 'white' in find_square_by_number_adress(position[0] + 1, position[1] + 1, board_state):
                    legal.append(num_adress_to_letter(position) + num_adress_to_letter([position[0] + 1, position[1] + 1]))
            if 0 <= position[1] - 1 <= 7:
                if color == 'white' and 'black' in find_square_by_number_adress(position[0] - 1, position[1] - 1, board_state):
                    legal.append(num_adress_to_letter(position) + num_adress_to_letter([position[0] - 1, position[1] - 1]))
            if 0 <= position[1] + 1 <= 7:
                if color == 'white' and 'black' in find_square_by_number_adress(position[0] - 1, position[1] + 1, board_state):
                    legal.append(num_adress_to_letter(position) + num_adress_to_letter([position[0] - 1, position[1] + 1]))
            #en passant
        if 'knight' in piece:
            legal += legal_moves_all_direction_pieces(knight_directions, 1, piece, board_state)
        if 'bishop' in piece:
            legal += legal_moves_all_direction_pieces(bishop_directions, 8, piece, board_state)
        if 'rook' in piece:
            legal += legal_moves_all_direction_pieces(rook_directions, 8, piece, board_state)
        if 'queen' in piece:
            legal += legal_moves_all_direction_pieces(rook_directions + bishop_directions, 8, piece, board_state)
        if 'king' in piece:
            legal += legal_moves_all_direction_pieces(rook_directions + bishop_directions, 1, piece, board_state)
    #delete illegal moves
    return legal

def is_check(attacker, board_state):
    king = ''
    if attacker == 'white':
        king = 'black_king'
    if attacker == 'black':
        king = 'white_king'
    attackers_legal_moves = legal_moves(attacker, board_state, check_matters=False)
    king_position = find_square_by_piece(king, board_state)
    king_position_letter = num_adress_to_letter(king_position)
    for move in attackers_legal_moves:
        if king_position_letter in move:   #attacker can lands on the king's square
            return True
    return False

def play_vs_ai(board_state):
    display_with_gui(board_state)


    while True:
        m = get_move_from_gui('white', board_state)
        board_state = execute_move(m, board_state)
        display_with_gui(board_state)
        b_l = legal_moves('black', board_state)
        m = choice(b_l)
        clock.tick(0.5)
        board_state = execute_move(m, board_state)
        display_with_gui(board_state)

play_vs_ai(board_state)
