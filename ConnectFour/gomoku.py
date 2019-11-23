import numpy as np
import time as time
import random as rand


class Gomoku:

    def __init__(self, size, in_a_row):
        self.size = size
        self.in_a_row = in_a_row
        self.board = np.zeros([size, size]).flatten()

    def is_winning_move(self, board, size, in_a_row, player, move):
        # Takes in a single move (x, y) and checks if there is a row, column, diagonal
        # or negative diagonal branching off that move
        # Checks only for the given player
        # Does not check the entire board
        x, y = move
        # ROW
        # Iterates to the right (i1) then to the left (i2) of (x, y) checking for a win
        # l counts the total length of the segment, if l == in_a_row then player has won
        l, i1, i2 = 1, 1, 1
        while x + i1 < size and board[size*(x + i1) + y] == player:
            l += 1
            i1 += 1
        while x - i2 >= 0 and board[size*(x - i2) + y] == player:
            l += 1 
            i2 += 1
        if l >= in_a_row:
            return True
        # COL
        # Same idea as row
        l, j1, j2 = 1, 1, 1
        while y + j1 < size and board[size*x + y + j1] == player:
            l += 1
            j1 += 1
        while x - j2 >= 0 and board[size*x + y - j2] == player:
            l += 1 
            j2 += 1
        if l >= in_a_row:
            return True
        # DIAG
        # Same idea as row
        l, i1, j1, i2, j2 = 1, 1, 1, 1, 1
        while x + i1 < size and y + j1 < size and board[size*(x + i1) + y + j1] == player:
            l += 1
            i1 += 1
            j1 += 1
        while x - i2 >= 0 and y - j2 >= 0 and board[size*(x - i2) + y - j2] == player:
            l += 1 
            i2 += 1
            j2 += 1
        if l >= in_a_row:
            return True
        # NEG DIAG 
        # Same idea as row
        l, i1, j1, i2, j2 = 1, 1, 1, 1, 1
        while x + i1 < size and y - j1 >= 0 and board[size*(x + i1) + y - j1] == player:
            l += 1
            i1 += 1
            j1 += 1
        while x - i2 >= 0 and y + j2 < size and board[size*(x - i2) + y + j2] == player:
            l += 1
            i2 += 1
            j2 += 1
        if l >= in_a_row:
            return True
        
    def display_board(self, board, size):
        # Prints the board out to the terminal
        print('  ', end='')
        for i in range(size):
            if i < 10:
                print(' ' + str(i), end='')
            else:
                print(str(i) + "", end='')
        print()

        for i in range(size):
            if i < 10:
                print(str(i) + ' |', end='')
            else:
                print(str(i) + '|', end='')
            for j in range(size):
                if board[size*i + j] == 1:
                    print('X|', end='')
                elif board[size*i + j] == -1:
                    print('O|', end='')
                else:
                    print('_|', end='')
            print(i)   

        print('  ', end='')
        for i in range(size):
            if i < 10:
                print(' ' + str(i), end='')
            else:
                print(str(i) + "", end='')
        print()
    
    def make_move(self, board, size, move, player):
        # Validates the move then makes it
        if 0 <= move[0] < size and 0 <= move[1] < size and board[size*move[0] + move[1]] == 0:
            board[size*move[0] + move[1]] = player
            return True
        return False

class Agent:

    def __init__(self, player, max_depth, radius, game):
        self.max_depth = max_depth
        self.player = player
        self.game = game
        self.M = game.size**2*game.in_a_row**3
        self.hash_table = {}
        #self.threat_scores = self.generate_threat_scores()

    #def generate_threat_scores(self):
    #    scores = {}
    #    for i in range(self.game.in_a_row):
    #        #open
    #        print(0)
    #        #close

    def get_best_move(self, board, size, in_a_row):
        # Rest hash table of previously seen boards
        self.hash_table = {}
        # Returns the best move for the agent
        return self.maxi(board, size, in_a_row, 0, float('-inf'), float('inf'), (-1, -1))    

    def maxi(self, board, size, in_a_row, depth, alpha, beta, last_move):
        
        # At depth 0 we return the best move and not just the value of the best move
        # Keeping track of the best move need only be done when we want to actually make the move
        # i.e. at depth 0
        # Other depths return only the value of the best move
        if depth == 0:
            moves = self.get_valid_moves(board, size)
            moves = self.threat_space_test(board, size, in_a_row, self.player, moves)[1:]
            # Ranks all moves with a score, then returns the highest scored move
            scores = sorted([
                (self.mini(board, size, in_a_row, depth + 1, alpha, beta, move), move) for move in moves
                ])[::-1]
            for score in scores:
                print(score)
            return scores[0][1]
        
        # If we are not at depth 0, we run regular mini-max
        # Make the move proposed at the previous depth, this is the last move of the opponent
        board[size*last_move[0] + last_move[1]] = -self.player
        # Check if we have seen and scored this board before
        # If we have, we simply retturn that score and dont need to compute anything further
        if tuple(board) in self.hash_table:
            val = self.hash_table[tuple(board)]
            board[size*last_move[0] + last_move[1]] = 0
            return val
        # Check if the move made by the opponent was a winning move
        # If so, we have lost
        if self.game.is_winning_move(board, size, in_a_row, -self.player, last_move):
            self.hash_table[tuple(board)] = -self.M + depth
            board[size*last_move[0] + last_move[1]] = 0
            return -self.M + depth
        # Check if our evalutation is complete
        # If so return a heursitic evaulation of the current board
        if depth == self.max_depth:
            val = -self.heuristic_eval(board, size, in_a_row, -self.player)
            self.hash_table[tuple(board)] = val
            board[size*last_move[0] + last_move[1]] = 0
            return val
        # If the game isnt over, we havent seen the board before, and we arent done searching
        # then we generate all the possible moves, remove irrelivant moves based on threats
        moves = self.get_valid_moves(board, size)
        if moves == []:
            return 0
        # Select only the moves with actual threats
        else:
            moves = self.threat_space_test(board, size, in_a_row, self.player, moves)[1:]
        best_val = float('-inf')
        # Check each move for its value
        for move in moves:
            # Recursive call to simulate our opponents next best move
            val = self.mini(board, size, in_a_row, depth + 1, alpha, beta, move)
            best_val = max(val, best_val)
            alpha = max(alpha, best_val)
            if alpha >= beta:
                break
        self.hash_table[tuple(board)] = best_val
        board[size*last_move[0] + last_move[1]] = 0
        return best_val

    def mini(self, board, size, in_a_row, depth, alpha, beta, last_move):
        # Make move of previous player (us)
        board[size*last_move[0] + last_move[1]] = self.player
        # Check if this position has been seen before
        # If it has, simply return the previously loged value
        if tuple(board) in self.hash_table:
            val = self.hash_table[tuple(board)]
            board[size*last_move[0] + last_move[1]] = 0
            return val
        # Check if the move we last made won the game
        if self.game.is_winning_move(board, size, in_a_row, self.player, last_move):
            self.hash_table[tuple(board)] = self.M - depth
            board[size*last_move[0] + last_move[1]] = 0
            return self.M - depth
        # Check if we are done searching
        # If we are, return a heuristic evaluation of the current position
        if depth == self.max_depth:
            val = self.heuristic_eval(board, size, in_a_row, self.player)
            self.hash_table[tuple(board)] = val
            board[size*last_move[0] + last_move[1]] = 0
            return val
        # If no one has won, we havent seen the position before, and we arent done searching
        # Then we iterate through all possible moves, remove the ones with no threats
        # and return the best move
        best_val = float('inf')
        moves = self.get_valid_moves(board, size)
        if moves == []:
            return 0
        else:
            # Remove moves that have no threat value
            moves = self.threat_space_test(board, size, in_a_row, -self.player, moves)[1:]
        for move in moves:
            # Recursive call to our response to the opponents move
            val = self.maxi(board, size, in_a_row, depth + 1, alpha, beta, move)
            best_val = min(val, best_val)
            beta = min(best_val, beta)
            if alpha >= beta:
                break
        # Save the value of this position
        self.hash_table[tuple(board)] = best_val
        # Undo move
        board[size*last_move[0] + last_move[1]] = 0
        return best_val
        
    def heuristic_eval(self, board, size, in_a_row, player):
        # Return some value that reprsents a 'good' guess of the value of the current position

        # Current version only checks values for the given player
        moves = self.get_valid_moves(board, size)
        val = self.threat_space_test(board, size, in_a_row, player, moves)[0]
        return val
        """
        for i in range(size):
            for j in range(size):
                # If the current square is occupied by the player
                # We give value sum(k^k for k = 1 to length of chain)
                if board[size*i + j] == player:
                    k = 1
                    while i + k < size and board[size*(i + k) + j] == player:
                        val += k*k
                        k+= 1
                    k = 1
                    while j + k < size and board[size*i + j + k] == player:
                        val += k*k
                        k+= 1
                    k = 1
                    while i + k < size and j + k < size and board[size*(i + k) + j + k] == player:
                        val += k*k
                        k+= 1
                    k = 1
                    while i + k < size and j - k >= 0 and board[size*(i + k) + j - k] == player:
                        val += k*k
                        k+= 1
        return val
        """

    def get_valid_moves(self, board, size):
        moves = []
        # All combinations that get us a square 1 radius away
        mods = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1,), (1, -1), (-1, 1), (-1, -1))
        for i in range(size):
            for j in range(size):
                # Find empty square with one non-empty square next to it
                if board[size*i + j] == 0:
                    for m in mods:
                        if 0 <= i + m[0] < size and 0 <= j + m[1] < size and board[size*(i + m[0]) + j + m[1]] != 0:
                            moves.append((i, j))
                            break
        return moves

    def threat_search(self, board, size, in_a_row, player, moves):
        ############################
        ###########################
        ###### NOT COMPLETE #######
        ###########################
        ###########################
        
        ##############################################
        # NEED TO ADD THREAT SEARCH FOR BOTH PLAYERS #
        ##############################################
        threats = [[0, move] for move in moves]
        directions = ((1, 0), (0, 1), (1, 1), (1, -1))
        for i in range(len(moves)):
            x, y = moves[i]
            for d in directions:
                #################################
                ###### CHECKS PLAYERS THREATS ##
                ################################
                l, k1, k2 = 0, 1, 1
                p = player
                while 0 <= x + k1*d[0] < size and 0 <= y + k1*d[1] < size and board[size*(x + k1*d[0]) + y + k1*d[1]] == p:
                    k1 += 1
                    l += 1
                while 0 <= x - k2*d[0] < size and 0 <= y - k2*d[1] < size and board[size*(x - k2*d[0]) + y - k2*d[1]] == p:
                    k2 += 1
                    l += 1
                # open
                if (k2 == 1 and k1 > 1 and 0 <= x + k1*d[0] < size and 0 <= y + k1*d[1] < size and board[size*(x + k1*d[0]) + y + k1*d[1]] == 0) or \
                   (k1 == 1 and k2 > 1 and 0 <= x - k1*d[0] < size and 0 <= y - k2*d[1] < size and board[size*(x - k2*d[0]) + y + k2*d[1]] == 0):
                    print("open p1")
                    print(k2, k1)
                    print([board[size*(x -i*d[0]) + y-i*d[0]] for i in range(-k2, k1 + 1) ])
                    if l == 3:
                       print("four")
                       threats[i][0] += 100
                    else:
                        threats[i][0] += l + 1          
                # gaping
                elif k1 > 1 and k2 > 1 and 0 <= x + k1*d[0] < size and 0 <= y + k1*d[1] < size and 0 <= x - k2*d[0] < size and 0 <= y - k2*d[1] < size and \
                     board[size*(x + k1*d[0]) + y + k1*d[1]] == 0 and board[size*(x - k2*d[0]) + y - k2*d[1]] == 0:
                    print("gaping p1")
                    if l == 3:
                       print("four")
                       threats[i][0] += 100
                    else:
                        threats[i][0] += l + 1

                # gaping closed 
                #elif (k2 == 0 and 0 <= x + k1*d[0] < size and (0 <= y + k1*d[1] < size or board[size*(x + k1*d[0]) + y + k1*d[1]] == -player)):

                # closed
                elif (k2 == 1 and (x + k1*d[0] >= size or x + k1*d[0] < 0 or y + k1*d[1] >= size or y + k1*d[1] < 0 or board[size*(x + k1*d[0]) + y + k1*d[1]] == -p)) or \
                     (k1 == 1 and (x - k2*d[0] >= size or x - k2*d[0] < 0 or y - k2*d[1] >= size or y - k2*d[1] < 0 or board[size*(x - k2*d[0]) + y - k2*d[1]] == -p)):
                    print("closed p1")
                    if l == 3:
                       print("four")
                       threats[i][0] += 100
                    else:
                        threats[i][0] += l - 2  
                #######################################
                ######### CHECK OPTS THREATS ##########
                #######################################
                l, k1, k2 = 0, 1, 1
                p = -player
                while 0 <= x + k1*d[0] < size and 0 <= y + k1*d[1] < size and board[size*(x + k1*d[0]) + y + k1*d[1]] == p:
                    k1 += 1
                    l += 1
                while 0 <= x - k2*d[0] < size and 0 <= y - k2*d[1] < size and board[size*(x - k2*d[0]) + y - k2*d[1]] == p:
                    k2 += 1
                    l += 1
                # open
                if (k2 == 1 and k1 > 1 and 0 <= x + k1*d[0] < size and 0 <= y + k1*d[1] < size and board[size*(x + k1*d[0]) + y + k1*d[1]] == 0) or \
                   (k1 == 1 and k2 > 1 and 0 <= x - k1*d[0] < size and 0 <= y - k2*d[1] < size and board[size*(x - k2*d[0]) + y + k2*d[1]] == 0):
                    print("open p1")
                    print(k2, k1)
                    print([board[size*(x -i*d[0]) + y-i*d[0]] for i in range(-k2, k1 + 1) ])
                    if l == 3:
                       print("four")
                       threats[i][0] += 100
                    else:
                        threats[i][0] += l + 1               
                # gaping
                elif k1 > 1 and k2 > 1 and 0 <= x + k1*d[0] < size and 0 <= y + k1*d[1] < size and 0 <= x - k2*d[0] < size and 0 <= y - k2*d[1] < size and \
                     board[size*(x + k1*d[0]) + y + k1*d[1]] == 0 and board[size*(x - k2*d[0]) + y - k2*d[1]] == 0:
                    print("gaping p2")
                    if l == 3:
                       print("four")
                       threats[i][0] += 100
                    else:
                        threats[i][0] += l + 1  

                # gaping closed 
                #elif (k2 == 0 and 0 <= x + k1*d[0] < size and (0 <= y + k1*d[1] < size or board[size*(x + k1*d[0]) + y + k1*d[1]] == -player)):

                # closed
                elif (k2 == 1 and (x + k1*d[0] >= size or x + k1*d[0] < 0 or y + k1*d[1] >= size or y + k1*d[1] < 0 or board[size*(x + k1*d[0]) + y + k1*d[1]] == -p)) or \
                     (k1 == 1 and (x - k2*d[0] >= size or x - k2*d[0] < 0 or y - k2*d[1] >= size or y - k2*d[1] < 0 or board[size*(x - k2*d[0]) + y - k2*d[1]] == -p)):
                    print("closed p2")
                    if l == 3:
                       print("four")
                       threats[i][0] += 100
                    else:
                        threats[i][0] += l - 1

                # Sort moves and retun top 
                threats = sorted(threats)[::-1]
                #print(threats)
                return [m for s, m in threats[:len(threats)//2 + 1]]

    def threat_space_test(self, board, size, in_a_row, player, moves):
        ########################################################
        ########################################################
        ######## BAORDS SHOULD KEEP TRACK OF THREATS ###########
        ########################################################
        ########################################################

        counted = set()
        directions = ((1, 0), (0, 1), (1, 1), (-1, 1))

        self_threat_2 = set()
        self_threat_3 = set()

        opt_threat_2 = set()
        opt_threat_3 = set()
        opt_4s = []
        
        for i, j in moves:
            p = player #### Player 1 check
            if (i, j) not in counted:
                for d in directions:
                    l, k1, k2 = 0, 1, 1
                    while 0 <= i + k1*d[0] < size and 0 <= j + k1*d[1] < size and board[size*(i + k1*d[0]) + j + k1*d[1]] == p:
                        l += 1
                        k1 += 1
                    while 0 <= i - k2*d[0] < size and 0 <= j - k2*d[1] < size and board[size*(i - k2*d[0]) + j - k2*d[1]] == p:
                        l += 1
                        k2 += 1
                    if l >= 2:
                        if l == 4:
                            #if k1 > 1 and k2 > 2:
                            #    print("threat 3")
                            #    self.show_board_with_threat(board, (i, j))
                            return [4, (i, j)]
                        elif l == 3:
                            if k1 == 1 and 0 <= i  - k2*d[0] < size and 0 <= j - k2*d[1] < size and board[size*(i - k2*d[0]) + j - k2*d[1]] == 0 or \
                               k2 == 1 and 0 <= i  + k1*d[0] < size and 0 <= j + k1*d[1] < size and board[size*(i + k1*d[0]) + j + k1*d[1]] == 0:
                                self_threat_3.add((i, j))
                                #print("threat 3")
                                #self.show_board_with_threat(board, (i, j))
                            elif k1 > 1 and k2 > 1 and 0 <= i - k2*d[0] < size and 0 <= j - k2*d[1] < size and 0 <= i + k1*d[0] < size and 0 <= j + k1*d[0] < size and \
                                 board[size*(i - k2*d[0]) + j - k2*d[1]] == 0 and board[size*(i + k1*d[0]) + j + k1*d[1]] == 0:
                                self_threat_3.add((i, j))
                                #print("threat 3")
                                #self.show_board_with_threat(board, (i, j))

                            else:
                                self_threat_2.add((i, j))
                                #print("threat 2")
                                #self.show_board_with_threat(board, (i, j))
                        elif l == 2:
                            if k1 == 1 and 0 <= i  - k2*d[0] < size and 0 <= j - k2*d[1] < size and board[size*(i - k2*d[0]) + j - k2*d[1]] == 0 or \
                               k2 == 1 and 0 <= i  + k1*d[0] < size and 0 <= j + k1*d[1] < size and board[size*(i + k1*d[0]) + j + k1*d[1]] == 0:
                                self_threat_2.add((i, j))
                                #print("threat 2")
                                #self.show_board_with_threat(board, (i, j))
                        counted.add((i, j))
                        
            if (i, j) not in counted:
                p = -player #### Player 2 check
                for d in directions:
                    l, k1, k2 = 0, 1, 1
                    while 0 <= i + k1*d[0] < size and 0 <= j + k1*d[1] < size and board[size*(i + k1*d[0]) + j + k1*d[1]] == p:
                        l += 1
                        k1 += 1
                    while 0 <= i - k2*d[0] < size and 0 <= j - k2*d[1] < size and board[size*(i - k2*d[0]) + j - k2*d[1]] == p:
                        l += 1
                        k2 += 1
                    if l >= 2:
                        if l == 4:
                            #if k1 > 1 and k2 > 2:
                            #    print("threat 3")
                            #    self.show_board_with_threat(board, (i, j))
                            opt_4s.append((i, j))
                        elif l == 3:
                            if k1 == 1 and 0 <= i  - k2*d[0] < size and 0 <= j - k2*d[1] < size and board[size*(i - k2*d[0]) + j - k2*d[1]] == 0 or \
                               k2 == 1 and 0 <= i  + k1*d[0] < size and 0 <= j + k1*d[1] < size and board[size*(i + k1*d[0]) + j + k1*d[1]] == 0:
                                opt_threat_3.add((i, j))
                                #print("threat 3")
                                #self.show_board_with_threat(board, (i, j))
                            elif k1 > 1 and k2 > 1 and 0 <= i - k2*d[0] < size and 0 <= j - k2*d[1] < size and 0 <= i + k1*d[0] < size and 0 <= j + k1*d[0] < size and \
                                 board[size*(i - k2*d[0]) + j - k2*d[1]] == 0 and board[size*(i + k1*d[0]) + j + k1*d[1]] == 0:
                                 opt_threat_3.add((i, j))
                                 #print("threat 3")
                                 #self.show_board_with_threat(board, (i, j)) ###### ADDED GAPPING THREEE #################
                            else:
                                opt_threat_2.add((i, j))
                                #print("threat 2")
                                #self.show_board_with_threat(board, (i, j))
                        elif l == 2:
                            if k1 == 1 and 0 <= i  - k2*d[0] < size and 0 <= j - k2*d[1] < size and board[size*(i - k2*d[0]) + j - k2*d[1]] == 0 or \
                               k2 == 1 and 0 <= i  + k1*d[0] < size and 0 <= j + k1*d[1] < size and board[size*(i + k1*d[0]) + j + k1*d[1]] == 0:
                                opt_threat_2.add((i, j))
                                #print("threat 2")
                                #self.show_board_with_threat(board, (i, j))
                        counted.add((i, j))
                
                    
        
        if opt_4s != []:
            return [3.5, opt_4s[0]]
        self_threat_3 = list(self_threat_3)
        if self_threat_3 != []:
            return [3] + self_threat_3
        opt_threat_3 = list(opt_threat_3)
        if opt_threat_3 != []:
            return [2.5] + opt_threat_3
        self_threat_2 = list(self_threat_2)
        opt_threat_2 = list(opt_threat_2)
        if self_threat_2 != [] or opt_threat_2 != []:
            return [2] + self_threat_2 + opt_threat_2
        if list(counted) == []:
            return [0] + rand.sample(moves, len(moves)//4)
        return [0] + list(counted)
        
    def show_board_with_threat(self, board, move):
        i, j = move
        print((i, j))
        for ii in range(size):
            print('|', end='')
            for jj in range(size):
                b = board[size*ii + jj]
                if ii == i and jj == j:
                    print('H|', end='')
                elif b == 0:
                    print('_|' , end='')
                elif b == 1:
                    print('X|', end='')
                elif b == -1:
                    print('O|', end='')
            print('')
                         








if __name__ == '__main__':
    size = 15
    in_a_row = 5
    max_depth = 11
    radius = 1

    game = Gomoku(size, in_a_row)
    agent1 = Agent(1, max_depth, radius, game)
    agent2 = Agent(-1, max_depth, radius, game)

    
    game.board[size*(size//2) + size//2] = 1
    game.display_board(game.board, game.size)

    while True:
        print("Player 2")
        move2 = agent2.get_best_move(game.board, game.size, game.in_a_row)
        #move2 = tuple([int(i) for i in input("x y: ").split()])
        game.make_move(game.board, game.size, move2, -1)
        game.display_board(game.board, game.size)
        if game.is_winning_move(game.board, game.size, game.in_a_row, -1, move2):
            print("player2 wins")
            break
    
    
        print("Player 1")
        move1 = agent1.get_best_move(game.board, game.size, game.in_a_row)
        game.make_move(game.board, game.size, move1, 1)
        game.display_board(game.board, game.size)
        if game.is_winning_move(game.board, game.size, game.in_a_row, 1, move1):
            print("player1 wins")
            break
    



























































