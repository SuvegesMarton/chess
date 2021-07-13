import pygame
import numpy as np
import cv2

import randommove
import minimax
import minimax_abp
import db_random
import db_mmabp

import pgn_interpreter

#F0D9B5; - 240, 217, 181
#946f51; - 148, 111, 81

KNIGHT_DIRECTIONS = [[2, 1], [2, -1], [1, 2], [1, -2], [-2, 1], [-2, -1], [-1, 2], [-1, -2]]
BISHOP_DIRECTIONS = [[1, 1], [-1, -1], [1, -1], [-1, 1]]
ROOK_DIRECTIONS = [[0, 1], [0, -1], [-1, 0], [1, 0]]


def copy_2d_list(list_to_copy):
    new_list = []
    for i in list_to_copy:
        new_list.append(i.copy())
    return new_list


def setup_board():
    #lower case means black pieces, upper case means white pieces
    pawns = ['p' for _ in range(8)]
    pieces = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
    board = [pieces, pawns]
    board += [['' for _ in range(8)] for _ in range(4)]
    board.append(uppercase_maker_for_setup(pawns))
    board.append(uppercase_maker_for_setup(pieces))
    return board


def flip_board(board_state):
    board_state.reverse()
    for line in board_state:
        line.reverse()
    return board_state


def setup_additional_board_info():
    #side to move, white can castle kingside, white can castle queenside, black can castle kingside, black can castle queenside, en passant target square
    return ['white', True, True, True, True, None]


def setup_by_FEN(fen):
    fen_chunks = fen.split(' ')
    lines_on_board = fen_chunks[0].split('/')
    #board setup
    board_setup = []
    for line in lines_on_board:
        new_line = []
        for char in line:
            if char in 'rnbqkpRNBQKP':
                new_line.append(char)
            else:
                new_line += ['' for _ in range(int(char))]
        board_setup.append(new_line)
    #additional info setup
        #side to move
    if fen_chunks[1] == 'w':
        additional_board_info = ['white']
    else:
        additional_board_info = ['black']
        #castling ability
    for i in fen_chunks[2]:
        if i == '-':
            additional_board_info.append(False)
        else:
            additional_board_info.append(True)
        #en passant target
    if fen_chunks[3] != '-':
        additional_board_info.append(fen_chunks[3])
    else:
        additional_board_info.append(None)
        #halfmove clock
    additional_board_info.append(fen_chunks[4])
        #full move counter
    additional_board_info.append(fen_chunks[5])

    return board_setup, additional_board_info


def FEN_by_setup(board_state, additional_board_info):
    full_fen = ''
    #board state
    board_string = ''
    for line in board_state:
        line_string = ''
        empty_counter = 0
        for square in line:
            if square == '':
                empty_counter += 1
            else:
                if empty_counter != 0:
                    line_string += str(empty_counter)
                    empty_counter = 0
                line_string += square
        if empty_counter != 0:
            line_string += str(empty_counter)
        board_string += line_string + '/'
    full_fen += board_string[:-1]
    #side to move
    if additional_board_info[0] == 'white':
        full_fen += ' w '
    else:
        full_fen += ' b '
    #castling ability
    if additional_board_info[1]:
        full_fen += 'K'
    if additional_board_info[2]:
        full_fen += 'Q'
    if additional_board_info[3]:
        full_fen += 'k'
    if additional_board_info[4]:
        full_fen += 'q'
    #en passant target square
    if additional_board_info[5] is None:
        full_fen += ' -'
    else:
        full_fen += ' ' + additional_board_info[5]
    #halfmove clock(50 moves rule)
    full_fen += ' ' + str(additional_board_info[6])
    #full move counter
    full_fen += ' ' + str(additional_board_info[7])


    return full_fen


def uppercase_maker_for_setup(lowercase_list):
    uppercase_list = []
    for i in lowercase_list:
        uppercase_list.append(i.upper())
    return uppercase_list


def get_move_from_gui(board_state, additional_board_info):
    color = additional_board_info[0]
    legals = legal_moves(board_state, additional_board_info)
    move_half_done = False
    first_half = 0
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                line, file = pos[1] // SQUARE_SIZE, pos[0] // SQUARE_SIZE
                if BOARD_FLIPPED:
                    line = 7 - line
                    file = 7 - file
                clicked_square = board_state[line][file]
                if move_half_done == True:
                    assembled_move = first_half + num_address_to_letter((line, file))
                    assembled_promotion_move = assembled_move + 'q'
                    if assembled_move in legals:
                        return assembled_move
                    if assembled_promotion_move in legals:
                        return assembled_promotion_move
                    elif (color == 'white' and clicked_square.isupper()) or (color == 'black' and clicked_square.islower()):
                        first_half = num_address_to_letter((line, file))
                        display_with_gui(board_state, selected_piece_position=[line, file], legal_moves=legals)
                    else:
                        move_half_done = False

                elif (color == 'white' and clicked_square.isupper()) or (color == 'black' and clicked_square.islower()):
                    first_half = num_address_to_letter((line, file))
                    move_half_done = True
                    display_with_gui(board_state, selected_piece_position=[line, file], legal_moves=legals)


def create_square_animation_map(square_num, board_state, legal_moves):
    #0 nothing
    #1 corners
    #2 green circle
    #3 check
    square_letter = num_address_to_letter(square_num)
    moves_to_animate = []
    for move in legal_moves:
        if move[:2] == square_letter:
            moves_to_animate.append(move)

    map = [[0 for i in range(8)] for i in range(8)]

    for i in moves_to_animate:
        if find_square_by_letter_address(i[2:], board_state) != '':
            num_address = letter_address_to_num(i[2:])
            map[num_address[0]][num_address[1]] = 1
        else:
            num_address = letter_address_to_num(i[2:])
            map[num_address[0]][num_address[1]] = 2
    return map


def apply_animation(img, animation_code):
    animation_code = int(animation_code)
    white = np.asarray([255, 255, 255])
    if animation_code == 0:
        return img
    elif animation_code == 1:
        squares_filter = cv2.imread('GUI/bases/corners.png')
        for i in range(len(squares_filter)):
            for j in range(len(squares_filter[i])):
                if not np.array_equal(squares_filter[i][j], white):
                    img[i][j] = squares_filter[i][j]
        return img
    elif animation_code == 2:
        circle_filter = cv2.imread('GUI/bases/middle_circle.png')
        for i in range(len(circle_filter)):
            for j in range(len(circle_filter[i])):
                if not np.array_equal(circle_filter[i][j], white):
                    img[i][j] = circle_filter[i][j]
        return img
    else:
        return img


def load_img(img_name):
    location = 'GUI/generated/' + img_name + '.png'
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
        figure_image = cv2.imread('GUI/bases/figures.png', cv2.IMREAD_COLOR)
        x, y, w, h = figure_coords[1]*200, figure_coords[0]*200, 200, 200
        figure_image = figure_image[y:y + h, x:x + w]

        white = np.asarray([255, 255, 255])
        black = np.asarray([0, 0, 0])

        for i in range(len(figure_image)):
            for j in range(len(figure_image[i])):
                if not(np.array_equal(figure_image[i][j], white)) and not(np.array_equal(figure_image[i][j], black)):
                    figure_image[i][j] = bg_color
    image = apply_animation(figure_image, img_name[-1])

    cv2.imwrite('GUI/generated/' + img_name + '.png', image)


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


def display_board_in_shell(board):
    for row in board:
        for square in row:
            print(square + ', ', end='')
        print('')


def display_with_gui(board, selected_piece_position=None, legal_moves=None):
    y = 0
    start_color = 1   #even = dark, odd = light
    if selected_piece_position != None:
        square_animation_map = create_square_animation_map(selected_piece_position, board, legal_moves)
        if BOARD_FLIPPED:
            square_animation_map = flip_board(square_animation_map)
    else:
        square_animation_map = [[0 for i in range(8)] for i in range(8)]
    if BOARD_FLIPPED:
        board = flip_board(copy_2d_list(board))
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


def num_address_to_letter(address):
    #input: 0-7
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    num = 8 - address[0]
    lett = letters[address[1]]
    return str(str(lett) + str(num))


def letter_address_to_num(address):
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    column = letters.index(address[0])
    row = 8 - int(address[1])
    return row, column


def find_square_by_letter_address(address, board_state):
    row, column = letter_address_to_num(address)
    return board_state[row][column]


def modify_additional_board_info(move, additional_board_info, change_side_to_move=True):
    if additional_board_info[0] == 'white' and change_side_to_move:
        additional_board_info[0] = 'black'
    elif additional_board_info[0] == 'black' and change_side_to_move:
        additional_board_info[0] = 'white'

    if 'a1' in move:
        additional_board_info[2] = False
    if 'e1' in move:
        additional_board_info[1] = False
        additional_board_info[2] = False
    if 'h1' in move:
        additional_board_info[1] = False
    if 'a8' in move:
        additional_board_info[3] = False
    if 'e8' in move:
        additional_board_info[3] = False
        additional_board_info[4] = False
    if 'h8' in move:
        additional_board_info[4] = False

    return additional_board_info


def modify_en_passant_target_square(new_target, additional_board_info):
    additional_board_info[5] = new_target
    return additional_board_info


def find_square_by_number_address(addressY, addressX, board_state):
    return board_state[addressY][addressX]


def is_square_attacked(square, board_state, additional_board_info, attacker_legal_moves=None):#square address input in letter format, does not work on attacker-color squares
    if attacker_legal_moves == None:
        attacker_legal_moves = legal_moves(board_state, additional_board_info, check_matters=False, check_castling=False)
    for move in attacker_legal_moves:
        if square == move[2:]:   #if attacker hits the square
            return True
    return False


def legal_moves_all_direction_pieces(directions, range, position, board_state):
    legals = []
    piece = find_square_by_number_address(position[0], position[1], board_state)
    for direction in directions:
        range_counter = 0
        new_position = position
        while range_counter < range:
            range_counter += 1
            new_position = [new_position[0] + direction[0], new_position[1] + direction[1]]
            if 0 > new_position[0] or new_position[0] > 7 or 0 > new_position[1] or new_position[1] > 7:
                break
            square = find_square_by_number_address(new_position[0], new_position[1], board_state)
            if square == '':
                legals.append(num_address_to_letter(position) + num_address_to_letter(new_position))
            elif square.isupper() != piece.isupper():
                legals.append(num_address_to_letter(position) + num_address_to_letter(new_position))
                break
            elif square.isupper() == piece.isupper():
                break
    return legals


def legal_moves_pawn(position, board_state, additional_board_info):
    legals = []
    pawn = board_state[position[0]][position[1]]
    if pawn.islower():
        forward_direction = [1, 0]
        capture_directions = [[1, 1], [1, -1]]
    else:
        forward_direction = [-1, 0]
        capture_directions = [[-1, 1], [-1, -1]]

    # capturing
    for dir in capture_directions:
        capture_square_position = [position[0] + dir[0], position[1] + dir[1]]
        if 0 <= capture_square_position[0] < 8 and 0 <= capture_square_position[1] < 8 and board_state[capture_square_position[0]][capture_square_position[1]] != '' and board_state[capture_square_position[0]][capture_square_position[1]].isupper() != pawn.isupper():
            move = num_address_to_letter(position) + num_address_to_letter(capture_square_position)
            if capture_square_position[0] == 7 or capture_square_position[0] == 0:
                legals += [move + 'q', move + 'r', move + 'n', move + 'b']
            else:
                legals.append(move)

    #moving forward
    forward_square_position = [position[0] + forward_direction[0], position[1] + forward_direction[1]]
    can_move_forward = False
    if 0 <= forward_square_position[0] < 8 and 0 <= forward_square_position[1] < 8 and board_state[forward_square_position[0]][forward_square_position[1]] == '':
        move = num_address_to_letter(position) + num_address_to_letter(forward_square_position)
        can_move_forward = True
        #promote
        if forward_square_position[0] == 7 or forward_square_position[0] == 0:
            legals += [move + 'q', move + 'r', move + 'n', move + 'b']
        else:
            legals.append(move)

    #double move
    if can_move_forward:
        double_forward_square_position = [forward_square_position[0] + forward_direction[0], forward_square_position[1] + forward_direction[1]]
        if 0 <= double_forward_square_position[0] < 8 and 0 <= double_forward_square_position[1] < 8 and board_state[double_forward_square_position[0]][double_forward_square_position[1]] == '':
            if (position[0] == 6 and pawn.isupper()) or (position[0] == 1 and pawn.islower()):
                move = num_address_to_letter(position) + num_address_to_letter(double_forward_square_position)
                legals.append(move)
    #en passant
    en_passant_target_square = additional_board_info[5]
    if en_passant_target_square != None:
        if num_address_to_letter([(position[0] + capture_directions[0][0]) % 8, (position[1] + capture_directions[0][1]) % 8]) == en_passant_target_square:
            legals.append(num_address_to_letter(position) + en_passant_target_square)
        if num_address_to_letter([(position[0] + capture_directions[1][0]) % 8, (position[1] + capture_directions[1][1]) % 8]) == en_passant_target_square:
            legals.append(num_address_to_letter(position) + en_passant_target_square)
    return legals


def castling(board_state, additional_board_info):
    legal_castling_moves = []
    side_to_move = additional_board_info[0]
    if side_to_move == 'white':
        can_castle = additional_board_info[1:3]
        attacker = 'black'
        line_number = 1
    else:
        can_castle = additional_board_info[3:5]
        attacker = 'white'
        line_number = 8

    modified_additional_board_info = [attacker] + additional_board_info[0:]

    attacker_legal_moves = None
    if can_castle[1]:#long castling
        attacker_legal_moves = legal_moves(board_state, modified_additional_board_info, check_castling=False, check_matters=False)
        squares_affected_by_king = ['c' + str(line_number), 'd' + str(line_number), 'e' + str(line_number)]
        squares_to_empty = ['b' + str(line_number), 'c' + str(line_number), 'd' + str(line_number)]
        none_under_attack = True
        all_empty = True
        for square in squares_affected_by_king:
            if is_square_attacked(square, board_state, additional_board_info, attacker_legal_moves=attacker_legal_moves):
                none_under_attack = False
                break
        for square in squares_to_empty:
            if find_square_by_letter_address(square, board_state) != '':
                all_empty = False
                break
        if none_under_attack and all_empty:
            legal_castling_moves.append('e' + str(line_number) + 'a' + str(line_number))
    if can_castle[0]:#short castling
        if attacker_legal_moves == None:
            attacker_legal_moves = legal_moves(board_state, modified_additional_board_info, check_castling=False, check_matters=False)
        squares_affected_by_king = ['e' + str(line_number), 'f' + str(line_number), 'g' + str(line_number)]
        squares_to_empty = ['f' + str(line_number), 'g' + str(line_number)]
        none_under_attack = True
        all_empty = True
        for square in squares_affected_by_king:
            if is_square_attacked(square, board_state, additional_board_info, attacker_legal_moves=attacker_legal_moves):
                none_under_attack = False
                break
        for square in squares_to_empty:
            if find_square_by_letter_address(square, board_state) != '':
                all_empty = False
                break
        if none_under_attack and all_empty:
            legal_castling_moves.append('e' + str(line_number) + 'h' + str(line_number))
    return legal_castling_moves


def execute_move(move, board_state, additional_board_info):
    board_state = copy_2d_list(board_state)
    additional_board_info = additional_board_info.copy()
    #castling
    if find_square_by_letter_address(move[:2], board_state) in ['k', 'K']:
        if move[:2] in ['e1', 'e8']:
            if move[2] == 'a':
                rook_square = letter_address_to_num('a' + move[1])
                b_file_square = letter_address_to_num('b' + move[1])
                new_king_square = letter_address_to_num('c' + move[1])
                new_rook_square = letter_address_to_num('d' + move[1])
                king_square = letter_address_to_num('e' + move[1])
                board_state[new_rook_square[0]][new_rook_square[1]] = find_square_by_number_address(*rook_square, board_state)
                board_state[new_king_square[0]][new_king_square[1]] = find_square_by_number_address(*king_square, board_state)
                board_state[rook_square[0]][rook_square[1]] = ''
                board_state[b_file_square[0]][b_file_square[1]] = ''
                board_state[king_square[0]][king_square[1]] = ''
                return board_state, modify_additional_board_info(move, additional_board_info)

            elif move[2] == 'h':
                rook_square = letter_address_to_num('h' + move[1])
                new_king_square = letter_address_to_num('g' + move[1])
                new_rook_square = letter_address_to_num('f' + move[1])
                king_square = letter_address_to_num('e' + move[1])
                board_state[new_rook_square[0]][new_rook_square[1]] = find_square_by_number_address(*rook_square, board_state)
                board_state[new_king_square[0]][new_king_square[1]] = find_square_by_number_address(*king_square, board_state)
                board_state[rook_square[0]][rook_square[1]] = ''
                board_state[king_square[0]][king_square[1]] = ''
                return board_state, modify_additional_board_info(move, additional_board_info)

    from_square = letter_address_to_num(move[:2])
    to = letter_address_to_num(move[2:])
    moving_piece = board_state[from_square[0]][from_square[1]]
    board_state[from_square[0]][from_square[1]] = ''
    #special pawn moves
    if moving_piece in ['p', 'P']:
        #en passant
        if move[0] != move[2] and board_state[to[0]][to[1]] == '':#if pawn, takes, empty square => en passant
            take_square = letter_address_to_num(str(move[2]) + str(move[1]))
            board_state[take_square[0]][take_square[1]] = ''

        board_state[to[0]][to[1]] = moving_piece
        #promotion
        if len(move) == 5:
            pawn_is_upper = moving_piece.isupper()
            while True:
                replacing_piece = move[4]#input('Promote the pawn to: ')
                if replacing_piece in ['r', 'n', 'b', 'q', 'R', 'N', 'B', 'Q']:
                    if pawn_is_upper:
                        moving_piece = replacing_piece.upper()
                    elif not pawn_is_upper:
                        moving_piece = replacing_piece
                    break
                else:
                    print('invalid piece code, try again!')
        #if double move, add target square behind the pawn
        if abs(int(move[1]) - int(move[3])) != 1:
            target_square_to_add = str(move[0]) + str(int((int(move[1]) + int(move[3])) / 2))#file same, rank between the start and arrival ranks of the pawn
            additional_board_info = modify_en_passant_target_square(target_square_to_add, additional_board_info)
        else:
            additional_board_info = modify_en_passant_target_square(None, additional_board_info)
    else:
        additional_board_info = modify_en_passant_target_square(None, additional_board_info)

    board_state[to[0]][to[1]] = moving_piece
    return board_state, modify_additional_board_info(move, additional_board_info)


def legal_moves(board_state, additional_board_info, check_matters=True, check_castling=True):
    color = additional_board_info[0]
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
                    legal += legal_moves_pawn(position, board_state, additional_board_info)
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
                        legal += castling(board_state, additional_board_info)
    #delete moves when the king is in check
    if check_matters:
        no_check_moves = []
        for move in legal:
            board_after_move, additional_board_info_after_move = execute_move(move, board_state, additional_board_info)
            if not is_check(board_after_move, [additional_board_info[0]] + additional_board_info_after_move[1:]):
                no_check_moves.append(move)
        legal = no_check_moves
    return legal


def is_check(board_state, additional_board_info):
    additional_board_info = additional_board_info.copy()
    if additional_board_info[0] == 'white':
        attacker = 'black'
    else:
        attacker = 'white'
    additional_board_info[0] = attacker
    king_position = [0, 0]
    for row in range(len(board_state)):
        for square in range(len(board_state[row])):
            if (board_state[row][square] == 'K' and attacker == 'black') or (board_state[row][square] == 'k' and attacker == 'white'):
                king_position = [row, square]
    attackers_legal_moves = legal_moves(board_state, additional_board_info, check_matters=False, check_castling=False)
    king_position_letter = num_address_to_letter(king_position)
    for move in attackers_legal_moves:
        if king_position_letter == move[2:]:   #if attacker hits the king's square
            return True
    return False


def is_checkmate(board_state, additional_board_info, surely_in_check=False):
    if surely_in_check:
        if len(legal_moves(board_state, additional_board_info)) == 0:
            return True
    if is_check(board_state, additional_board_info):
        if len(legal_moves(board_state, additional_board_info)) == 0:
            return True
    return False


def main(board_state=None, additional_board_info=None):
    # set basics if there is no specific position given
    if board_state == None:
        board_state = setup_board()
    if additional_board_info == None:
        additional_board_info = setup_additional_board_info()

    # if any of the player uses a database, load it
    db_random_handler, db_mmabp_handler = None, None
    if WHITE == 4 or BLACK == 4:
        db_random_handler = db_random.DatabaseHandler('./csv_database.csv')
    if WHITE == 5 or BLACK == 5:
        db_mmabp_handler = db_mmabp.DatabaseHandler('./csv_database.csv')


    moves_played = []


    display_with_gui(board_state)


    move = None
    while True:
        if additional_board_info[0] == 'white':
            if WHITE == 0:
                move = get_move_from_gui(board_state, additional_board_info)
            elif WHITE == 1:
                move = randommove.choose_move(board_state, additional_board_info)
            elif WHITE == 2:
                move, investigated_positions, dynamic_eval = minimax.find_best_move(board_state, additional_board_info, WHITE_DEPTH)
                print("number of investigated positions:", investigated_positions)
                print('dynamic eval:', dynamic_eval)
            elif WHITE == 3:
                move, investigated_positions, dynamic_eval = minimax_abp.find_best_move(board_state, additional_board_info, WHITE_DEPTH)
                print("number of investigated positions:", investigated_positions)
                print('dynamic eval:', dynamic_eval)
            elif WHITE == 4:
                move = db_random_handler.find_move_with_database(moves_played, board_state, additional_board_info, True)

            elif WHITE == 5:
                move = db_mmabp_handler.find_move_with_database(moves_played, board_state, additional_board_info, WHITE_DEPTH, True)


        elif additional_board_info[0] == 'black':
            if BLACK == 0:
                move = get_move_from_gui(board_state, additional_board_info)
            elif BLACK == 1:
                move = randommove.choose_move(board_state, additional_board_info)
            elif BLACK == 2:
                move, investigated_positions, dynamic_eval = minimax.find_best_move(board_state, additional_board_info, BLACK_DEPTH)
                print("number of investigated positions:", investigated_positions)
                print('dynamic eval:', dynamic_eval)
            elif BLACK == 3:
                move, investigated_positions, dynamic_eval = minimax_abp.find_best_move(board_state, additional_board_info, BLACK_DEPTH)
                print("number of investigated positions:", investigated_positions)
                print('dynamic eval:', dynamic_eval)
            elif BLACK == 4:
                move = db_random_handler.find_move_with_database(moves_played, board_state, additional_board_info, True)

            elif BLACK == 5:
                move = db_mmabp_handler.find_move_with_database(moves_played, board_state, additional_board_info, BLACK_DEPTH, True)

        board_state, additional_board_info = execute_move(move, board_state, additional_board_info)
        moves_played.append(move)
        display_with_gui(board_state)
        check = is_check(board_state, additional_board_info)
        checkmate = is_checkmate(board_state, additional_board_info)
        fen = FEN_by_setup(board_state, additional_board_info)
        print('move:', move)
        print('position FEN:', fen)
        print('check:', check)
        print('checkmate:', checkmate)
        print('static eval:', round(minimax.static_evaluation(board_state), 3))
        print("\n")
        if checkmate:
            break


def display_game(moves, board_state=None, additional_board_info=None):
    if board_state == None:
        board_state = setup_board()
    if additional_board_info == None:
        additional_board_info = setup_additional_board_info()
    display_with_gui(board_state)
    for move in moves:
        board_state, additional_board_info = execute_move(move, board_state, additional_board_info)
        display_with_gui(board_state)
        clock.tick(1)


GAMEMODE = 0

# 0 = live game, 1 = game replay from database

BOARD_FLIPPED = True

WHITE = 3
BLACK = 5

# 0 = human player
# 1 = random moves - randommove.py
# 2 = bruteforce minimax algorithm - minimax.py
# 3 = minimax with alpha beta pruning - minimax_abp.py
# 4 = database first, then random moves - db_random.py
# 5 = database first, then minimax with alpha beta pruning - db_mmabp.py


WHITE_DEPTH = 2
BLACK_DEPTH = 2
# depth matters only if the player is engine

if __name__ == "__main__":
    WITH_GUI = True
    if WITH_GUI:
        SQUARE_SIZE = 100
        pygame.init()
        gameDisplay = pygame.display.set_mode((SQUARE_SIZE * 8, SQUARE_SIZE * 8))
        pygame.display.set_caption('Chess')
        clock = pygame.time.Clock()
    if GAMEMODE == 0:
        board_state, additional_board_info = setup_by_FEN('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        main(board_state=board_state, additional_board_info=additional_board_info)
    elif GAMEMODE == 1:
        game_to_replay = pgn_interpreter.translate_pgn_move_chain_in_position(pgn_interpreter.load_pgn_file('pgn_database/Wei Yi.pgn')[0].moves)
        display_game(game_to_replay)