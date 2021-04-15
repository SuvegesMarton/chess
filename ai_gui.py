import pygame
import numpy as np
import cv2
from random import randint, choice
#F0D9B5; - 240, 217, 181
#946f51; - 148, 111, 81

def copy_2d_list(list_to_copy):
    new_list = []
    for i in list_to_copy:
        new_list.append(i.copy())
    return new_list

def setup_board():
    #lower case means black pieces, upper case means white pieces
    pawns = ['p' for _ in range(8)]
    pieces = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
    if BOARD_FLIPPED == False:
        board = [pieces, pawns]
        board += [['' for _ in range(8)] for _ in range(4)]
        board.append(uppercase_maker_for_setup(pawns))
        board.append(uppercase_maker_for_setup(pieces))
        return board
    if BOARD_FLIPPED == True:
        pieces.reverse()
        board = [uppercase_maker_for_setup(pieces), uppercase_maker_for_setup(pawns)]
        board += [['' for _ in range(8)] for _ in range(4)]
        board.append(pawns)
        board.append(pieces)
        return board

def uppercase_maker_for_setup(lowercase_list):
    uppercase_list = []
    for i in lowercase_list:
        uppercase_list.append(i.upper())
    return uppercase_list

def get_move_from_gui(color, board_state, additional_board_info):
    #print('before', board_state)
    legals = legal_moves(color, board_state, additional_board_info)
    #print('after', board_state)
    move_half_done = False
    first_half = 0
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                line, file = pos[1] // SQUARE_SIZE, pos[0] // SQUARE_SIZE
                clicked_square = board_state[line][file]
                if move_half_done == True:
                    assembled_move = first_half + num_adress_to_letter((line, file))
                    if assembled_move in legals:
                        return assembled_move
                    elif (color == 'white' and clicked_square.isupper()) or (color == 'black' and clicked_square.islower()):
                        first_half = num_adress_to_letter((line, file))
                        display_with_gui(board_state, selected_piece_position=[line, file], legal_moves=legals)
                    else:
                        move_half_done = False

                elif (color == 'white' and clicked_square.isupper()) or (color == 'black' and clicked_square.islower()):
                    first_half = num_adress_to_letter((line, file))
                    move_half_done = True
                    display_with_gui(board_state, selected_piece_position=[line, file], legal_moves=legals)

def create_square_animation_map(square_num, board_state, legal_moves):
    #0 nothing
    #1 corners
    #2 green circle
    #3 check
    square_letter = num_adress_to_letter(square_num)
    moves_to_animate = []
    for move in legal_moves:
        if move[:2] == square_letter:
            moves_to_animate.append(move)

    map = [[0 for i in range(8)] for i in range(8)]

    for i in moves_to_animate:
        if find_square_by_letter_adress(i[2:], board_state) != '':
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
    img = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))
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
        print(img_name)
        create_img(img_name)
        img = load_img(img_name)
    return img

def img_format_name_from_square(square):
    if square.isupper():
        piece_color = '1'
    elif square.islower():
        piece_color = '0'
    else:
        piece_color = 'e'
    square.islower()
    if square != '':
        piece_name = square.lower()
    else:
        piece_name = 'e'
    return piece_color + piece_name

def display_board(board):
    for row in board:
        for square in row:
            print(square + ', ', end='')
        print('')

def display_with_gui(board, selected_piece_position=None, legal_moves=None):
    y = 0
    start_color = 1   #even = dark, odd = light
    if selected_piece_position != None:
        square_animation_map = create_square_animation_map(selected_piece_position, board, legal_moves)
    else:
        square_animation_map = [[0 for i in range(8)] for i in range(8)]
    for i, row in enumerate(board):
        x = 0
        square_color = start_color
        for j, square in enumerate(row):
            img_name = img_format_name_from_square(square) + str(square_color%2) + str(square_animation_map[i][j])
            img = get_image(img_name)
            gameDisplay.blit(img, (x, y))
            x += SQUARE_SIZE
            square_color += 1
        start_color += 1
        y += SQUARE_SIZE
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
    row, column = letter_adress_to_num(adress)
    return board_state[row][column]

def find_square_by_piece(piece, board_state):
    for i, row in enumerate(board_state):
        if piece in row:
            return [i, row.index(piece)]
    return None

def find_square_by_number_adress(adressY, adressX, board_state):
    return board_state[adressY][adressX]

def legal_moves_all_direction_pieces(directions, range, position, board_state):
    legals = []
    piece = find_square_by_number_adress(position[0], position[1], board_state)
    for direction in directions:
        range_counter = 0
        new_position = position
        while range_counter < range:
            range_counter += 1
            new_position = [new_position[0] + direction[0], new_position[1] + direction[1]]
            if 0 > new_position[0] or new_position[0] > 7 or 0 > new_position[1] or new_position[1] > 7:
                break
            square = find_square_by_number_adress(new_position[0], new_position[1], board_state)
            if square == '':
                legals.append(num_adress_to_letter(position) + num_adress_to_letter(new_position))
            elif square.isupper() != piece.isupper():
                legals.append(num_adress_to_letter(position) + num_adress_to_letter(new_position))
                break
            elif square.isupper() == piece.isupper():
                break
    return legals

def legal_moves_pawn(position, board_state, previous_move):
    legals = []
    pawn = board_state[position[0]][position[1]]
    if (BOARD_FLIPPED == False and pawn.islower()) or (BOARD_FLIPPED == True and pawn.isupper()):
        forward_direction = [1, 0]
        capture_directions = [[1, 1], [1, -1]]
    else:
        forward_direction = [-1, 0]
        capture_directions = [[-1, 1], [-1, -1]]

    #moving forward
    forward_square_position = [position[0] + forward_direction[0], position[1] + forward_direction[1]]
    can_move_forward = False
    if 0 <= forward_square_position[0] < 8 and 0 <= forward_square_position[1] < 8 and board_state[forward_square_position[0]][forward_square_position[1]] == '':
        move = num_adress_to_letter(position) + num_adress_to_letter(forward_square_position)
        legals.append(move)
        can_move_forward = True
    #capturing
    for dir in capture_directions:
        capture_square_position = [position[0] + dir[0], position[1] + dir[1]]
        if 0 <= capture_square_position[0] < 8 and 0 <= capture_square_position[1] < 8 and board_state[capture_square_position[0]][capture_square_position[1]] != '' and board_state[capture_square_position[0]][capture_square_position[1]].isupper() != pawn.isupper():
            move = num_adress_to_letter(position) + num_adress_to_letter(capture_square_position)
            legals.append(move)
    #double move
    if can_move_forward:
        double_forward_square_position = [forward_square_position[0] + forward_direction[0], forward_square_position[1] + forward_direction[1]]
        if 0 <= double_forward_square_position[0] < 8 and 0 <= double_forward_square_position[1] < 8 and board_state[double_forward_square_position[0]][double_forward_square_position[1]] == '':
            if position[0] == 6 and ((pawn.isupper() and not BOARD_FLIPPED) or (pawn.islower() and BOARD_FLIPPED)) or position[0] == 1 and ((pawn.islower() and not BOARD_FLIPPED) or (pawn.isupper() and BOARD_FLIPPED)):
                move = num_adress_to_letter(position) + num_adress_to_letter(double_forward_square_position)
                legals.append(move)
    #en passant
    if previous_move == None:
        pass
    elif find_square_by_letter_adress(previous_move[2:], board_state) in ['p', 'P']:#pawn moved
        if abs(int(previous_move[1]) - int(previous_move[3])) == 2:#two squares forward
            pawn_position = letter_adress_to_num(previous_move[2:])
            if pawn_position[0] == position[0] and abs(int(pawn_position[1]) - int(position[1])) == 1:#next to each other
                take_position = previous_move[0] + str(int((int(previous_move[1]) + int(previous_move[3])) / 2))
                move = num_adress_to_letter(position) + take_position
                legals.append(move)
    return legals

def castling(board_state, side_to_move, additional_board_info):
    pass

def execute_move(move, board_state):
    from_square = letter_adress_to_num(move[:2])
    to = letter_adress_to_num(move[2:])
    moving_piece = board_state[from_square[0]][from_square[1]]
    board_state[from_square[0]][from_square[1]] = ''
    #captured = board_state[to[0]][to[1]]
    # en passant
    if moving_piece in ['p', 'P'] and move[0] != move[2] and board_state[to[0]][to[1]] == '':#if pawn, takes, empty square => en passant
        take_square = letter_adress_to_num(str(move[2]) + str(move[1]))
        board_state[take_square[0]][take_square[1]] = ''

    board_state[to[0]][to[1]] = moving_piece
    #promotion
    if moving_piece in ['p', 'P'] and (to[0] == 0 or to[0] == 7):
        pawn_is_upper = moving_piece.isupper()
        while True:
            replacing_piece = 'q'#input('Promote the pawn to: ')
            if replacing_piece in ['r', 'n', 'b', 'q']:
                if pawn_is_upper:
                    replacing_piece = replacing_piece.upper()
                board_state[to[0]][to[1]] = replacing_piece
                break
            else:
                print('invalid piece code, try again!')


    return board_state

def legal_moves(color, board_state, additional_board_info, check_matters=True, check_castling=True):
    legal = []
    #find moves
    for row in range(len(board_state)):
        for column in range(len(board_state[row])):
            square = board_state[row][column]
            if square == '':#if square is empty
                continue
            elif square.isupper() and color == 'white' or square.islower() and color == 'black':#if the piece on the square belongs to the player who will make the move
                square = square.lower()
                position = [row, column]
                if square == 'p':
                    legal += legal_moves_pawn(position, board_state, additional_board_info['previous_move'])
                if square == 'n':
                    legal += legal_moves_all_direction_pieces(KNIGHT_DIRECTIONS, 1, position, board_state)
                if square == 'b':
                    legal += legal_moves_all_direction_pieces(BISHOP_DIRECTIONS, 8, position, board_state)
                if square == 'r':
                    legal += legal_moves_all_direction_pieces(ROOK_DIRECTIONS, 8, position, board_state)
                if square == 'q':
                    legal += legal_moves_all_direction_pieces(ROOK_DIRECTIONS + BISHOP_DIRECTIONS, 8, position, board_state)
                if square == 'k':
                    legal += legal_moves_all_direction_pieces(ROOK_DIRECTIONS + BISHOP_DIRECTIONS, 1, position, board_state)
                    if check_castling:
                        pass
    #delete moves when the king is in check
    if check_matters:
        no_check_moves = []
        for move in legal:
            board_after_move = execute_move(move, copy_2d_list(board_state))
            attacker = ''
            if color == 'white':
                attacker = 'black'
            if color == 'black':
                attacker = 'white'
            if not is_check(attacker, board_after_move, additional_board_info):
                no_check_moves.append(move)
        legal = no_check_moves
    return legal

def is_check(attacker, board_state, additional_board_info):
    king_position = [0, 0]
    for row in range(len(board_state)):
        for square in range(len(board_state[row])):
            if (board_state[row][square] == 'K' and attacker == 'black') or (board_state[row][square] == 'k' and attacker == 'white'):
                king_position = [row, square]
    attackers_legal_moves = legal_moves(attacker, board_state, additional_board_info, check_matters=False, check_castling=False)
    king_position_letter = num_adress_to_letter(king_position)
    for move in attackers_legal_moves:
        if king_position_letter in move:   #attacker can lands on the king's square
            return True
    return False

def play_vs_ai(board_state=None, additional_board_info=None):
    if board_state == None:
        board_state = setup_board()
    if additional_board_info == None:
        additional_board_info = {
            'previous_move': None,
            'black_rooks_moved': [False, False],
            'black_king_moved': False,
            'white_rooks_moved': False,
            'white_king_moved': False,
        }
    display_with_gui(board_state)
    while True:
        if BOARD_FLIPPED:
            w_l = legal_moves('white', board_state, additional_board_info)
            m = choice(w_l)
        else:
            m = get_move_from_gui('white', board_state, additional_board_info)
        board_state = execute_move(m, board_state)
        additional_board_info['previous_move'] = m
        display_with_gui(board_state)
        if BOARD_FLIPPED:
            m = get_move_from_gui('black', board_state, additional_board_info)
        else:
            b_l = legal_moves('black', board_state, additional_board_info)
            m = choice(b_l)
        board_state = execute_move(m, board_state)
        additional_board_info['previous_move'] = m
        display_with_gui(board_state)

def pvp(board_state=None, additional_board_info=None):
    if board_state == None:
        board_state = setup_board()
    if additional_board_info == None:
        additional_board_info = {
            'previous_move': None,
            'black_rooks_moved': [False, False],
            'black_king_moved': False,
            'white_rooks_moved': False,
            'white_king_moved': False,
        }
    display_with_gui(board_state)
    while True:
        m = get_move_from_gui('white', board_state, additional_board_info)
        board_state = execute_move(m, board_state)
        additional_board_info['previous_move'] = m
        print(is_check('white', board_state, additional_board_info))
        display_with_gui(board_state)
        m = get_move_from_gui('black', board_state, additional_board_info)
        board_state = execute_move(m, board_state)
        additional_board_info['previous_move'] = m
        print(is_check('black', board_state, additional_board_info))

        display_with_gui(board_state)
        
BOARD_FLIPPED = False

KNIGHT_DIRECTIONS = [[2, 1], [2, -1], [1, 2], [1, -2], [-2, 1], [-2, -1], [-1, 2], [-1, -2]]
BISHOP_DIRECTIONS = [[1, 1], [-1, -1], [1, -1], [-1, 1]]
ROOK_DIRECTIONS = [[0, 1], [0, -1], [-1, 0], [1, 0]]

WITH_GUI = True
if WITH_GUI:
    SQUARE_SIZE = 100
    pygame.init()
    gameDisplay = pygame.display.set_mode((SQUARE_SIZE*8, SQUARE_SIZE*8))
    pygame.display.set_caption('Chess')
    clock = pygame.time.Clock()

#play_vs_ai(board_state, additional_board_info)
pvp()
