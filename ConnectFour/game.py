import numpy as np
import pygame as pg
import time as time
import random as rand
# pylint: disable=no-name-in-module
from pygame.constants import (MOUSEBUTTONDOWN, MOUSEMOTION, QUIT)
# pylint: enable=no-name-in-module

def game_over(board, n, in_a_row, player, disp=False):
    for i in range(n):
        for j in range(n):
            if board[i][j] == player:
                # Check surrounding lines for a win
                # ROWS
                if i + in_a_row - 1 < n:
                    if sum([board[i + x][j] for x in range(in_a_row)]) == player*in_a_row:
                        if disp:
                            print(i, j, "row")
                            print([board[i + x][j] for x in range(in_a_row)])
                        return True
                # COLUMNS
                if j + in_a_row - 1 < n:
                    if sum([board[i][j + y] for y in range(in_a_row)]) == player*in_a_row:
                        if disp:
                            print(i, j, "col")
                            print([board[i][j + y] for y in range(in_a_row)])
                        return True
                # DIAGONAL x == y
                if i + in_a_row - 1 < n and j + in_a_row - 1 < n:
                    if sum([board[i + x][j + x] for x in range(in_a_row)]) == player*in_a_row:
                        if disp:
                            print(i, j, "diag")
                            print([board[i + x][j + x] for x in range(in_a_row)])
                        return True
                # DIAGONAL x == -y
                if i + in_a_row  - 1 < n and j - in_a_row  + 1 >= 0:
                    if sum([board[i + x][j - x] for x in range(in_a_row)]) == player*in_a_row:
                        if disp:
                            print(i, j, 'neg diag')
                            print([board[i + x][j - x] for x in range(in_a_row)])
                        return True
    return False    

def is_winning_move(board, n, move, in_a_row, player):
    x = move[0]
    y = move[1]
    # ROW
    print("Rand")
    l, i1, i2 = 1, 1, 1
    while x + i1 < n and board[x + i1][y] == player:
        i1 += 1
        l += 1
    while x - i2 >= 0 and board[x - i1][y] == player:
        i2 += 1
        l += 1
    if l >= in_a_row:
        return True
    # COL
    l, j1, j2 = 1, 1, 1
    while y + j1 < n and board[x][y + j1] == player:
        j1 + 1
        l += 1
    while y - j2 >= 0 and board[x][y - j2] == player:
        j2 += 1
        l += 1
    if l >= in_a_row:
        return True
    # DIAG
    l, i1, i2, j1, j2 = 1, 1, 1, 1, 1
    while x + i1 < n and y + j1 < n and board[x + i1][y + j1] == player:
        i1 += 1
        j1 += 1
        l += 1
    while x - i2 >=0 and y - j2 >= 0 and board[x - i2][y - j2] == player:
        i2 += 1
        j2 += 1
        l += 1
    if l >= in_a_row:
        return True
    # NEG DIAG
    l, i1, i2, j1, j2 = 1, 1, 1, 1, 1
    while x + i1 < n and y - j1 >= 0 and board[x + i1][y - j1] == player:
        i1 += 1
        j1 += 1
        l += 1
    while x - i2 >= 0 and y + j2 < n and board[x - i2][y + j2] == player:
        i2 += 1
        j2 += 1
        l += 1
    if l >= in_a_row:
        return True

def make_move(board, n, column, player):
    if board[0][column] != 0:
        return False
    for row in range(n):
        if board[n - row - 1][column] == 0:
            board[n - row - 1][column] = player
            return True

def player_move(player):
    return False

def ai_move(board, n, max_depth, player):
    moves = get_valid_c4_moves(board, n)
    best_val = float("-inf")
    best_move = moves[rand.randint(0, len(moves) - 1)]
    alpha = float('-inf')
    beta = float('inf')
    for move in moves:
        val = mini(board, n, move, 0, max_depth, (-1)*player, alpha, beta)
        print(player, move, val)
        if val > best_val:
            best_val = val
            best_move = move
            alpha = max(alpha, best_val)
            if alpha > beta:
                #print(alpha, beta)
                break
    return best_move 

def maxi(board, n, move, depth, max_depth, player, alpha, beta):
    board[move[0]][move[1]] = (-1)*player
    if is_winning_move(board, n, move, in_a_row, (-1)*player):
        board[move[0]][move[1]] = 0
        return float('-inf')
    if depth == max_depth:
        board[move[0]][move[1]] = 0
        return -heur_eval(board, n, player)

    moves = get_valid_c4_moves(board, n)
    if len(moves) == 0:
        return 0

    best_val = float('-inf')
    for move in moves:
        val = mini(board, n, move, depth + 1, max_depth, (-1)*player, alpha, beta)
        
        best_val = max(val, best_val)
        alpha = max(alpha, best_val)
        if alpha > beta:
            #print(alpha, beta)
            break
    # reverse move
    board[move[0]][move[1]] = 0
    return best_val

def mini(board, n, move, depth, max_depth, player, alpha, beta):
    board[move[0]][move[1]] = (-1)*player
    if is_winning_move(board, n, move, in_a_row, (-1)*player):
        board[move[0]][move[1]] = 0
        return float('inf')
    if depth == max_depth:
        board[move[0]][move[1]] = 0
        return heur_eval(board, n, player)

    moves = get_valid_c4_moves(board, n)
    if len(moves) == 0:
        return 0

    best_val = float('inf')
    for move in moves:
        val = maxi(board, n, move, depth + 1, max_depth, (-1)*player, alpha, beta)
        
        best_val = min(val, best_val)
        beta = min(beta, best_val)
        if alpha > beta:
            #print(alpha, beta)
            break
    # Reverse move
    board[move[0]][move[1]] = 0
    return best_val

def get_valid_c4_moves(board, n):
    
    moves = []
    for col in range(n):
        if board[0][col] == 0:
            for i in range(n):
                if board[n - i - 1][col] == 0:
                    moves.append((n - i - 1, col))
                    break
    return moves

def heur_eval(board, n, player):
    ####################################
    ####################################
    ####################################
    ######### CHANGE ###################
    val = 0
    for i in range(n):
        for j in range(n):
            k = 1
            if board[i][j] == player:
                k = 1
                while i + k < n and board[i + k][j] == player:
                    val += 2**k
                    k += 1

                k = 1
                while j + k < n and board[i][j + k] == player:
                    val += 2**k
                    k += 1

                k = 1
                while i + k < n and j + k < n and board[i + k][j + k] == player:
                    val += 2**k
                    k += 1

                k = 1
                while i + k < n and i - k >= 0 and board[i + k][j - k] == player:
                    val += 2**k
                    k += 1
    return val
                
############ VISUALS ##################
#######################################
def update_board_display(move, player):
    if player == 1:
        pg.draw.circle(screen, (255, 255, 0), grid[move[0]][move[1]], radius)
    else:
        pg.draw.circle(screen, (255, 0, 0), grid[move[0]][move[1]], radius)
    pg.display.update()

def display_board_text(board, n):
    
    for i in range(n):
        print('|', end='')
        for j in range(n):
            if board[i][j] == 0:
                print('_|', end='')
            elif board[i][j] == 1:
                print('X|', end='')
            elif board[i][j] == -1:
                print('O|', end='')
        print()






width = 800
height = 800
size = (width, height)
board_size = 6
radius = width//board_size//2 - 2


grid = [[(int(width/board_size*(i + 0.5)), int(height/board_size*(j + 0.5))) for i in range(board_size)] for j in range(board_size)]
board = np.zeros([board_size, board_size])


# Initalize pygame parameters
# pylint: disable=no-member 
pg.init() 
# pylint: enable=no-member
screen = pg.display.set_mode(size)
pg.display.update()
myfont = pg.font.SysFont("monospace", 75)

# Draw inital board
pg.draw.rect(screen, (0, 0, 255), (0, 0, width, height))
for row in grid:
    for x, y in row:
        pg.draw.circle(screen, (0, 0, 0), (x, y), radius)
pg.display.update()

"""
# Game loop
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()
        if event.type == pg.MOUSEBUTTONDOWN:
            print(event.pos)

            col = int(board_size*event.pos[0]/ width) 
            row = board_size - 1
            while board[row][col] != 0.0:
                row -= 1
            print(board)
            print(row, col)
            pg.draw.circle(screen, (255, 0, 0), grid[row][col], radius)
            board[row][col] = 1
            pg.display.update()
"""

in_a_row = 4
not_over = True
max_depth = 3
n = len(board)
while not_over: 
    for event in pg.event.get():
        if event.type == MOUSEBUTTONDOWN:  
            move = ai_move(board, n, max_depth, 1)
            board[move[0]][move[1]] = 1
            if game_over(board, n, in_a_row, 1, disp=True):
                print("player1 wins")
                not_over = False
            update_board_display(move, 1)
            print("#################################")
    
            move = ai_move(board, n, max_depth, -1)
            board[move[0]][move[1]] = -1
            if game_over(board, n, in_a_row, -1, disp=True):
                print("player2 wins")
                not_over = False
            update_board_display(move, -1)
            print("#################################")

            display_board_text(board, n)
            print(board)
        
print("OUT")
while True:
    for event in pg.event.get():
        if event.type == QUIT:
            # pylint: disable=no-member 
            pg.quit() 
            # pylint: enable=no-member
            exit()
        if event.type == MOUSEMOTION:
            pg.display.update()
