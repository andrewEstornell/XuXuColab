import numpy as np
import time as time


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
        for i in range(size):
            print('|', end='')
            for j in range(size):
                if board[size*i + j] == 1:
                    print('X|', end='')
                elif board[size*i + j] == -1:
                    print('O|', end='')
                else:
                    print('_|', end='')
            print('')        

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
            moves = self.threat_search(board, size, in_a_row, self.player, moves)
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
            val = -self.heuristic_eval(board, size, -self.player)
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
            moves = self.threat_search(board, size, in_a_row, self.player, moves)
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
            val = self.heuristic_eval(board, size, self.player)
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
            moves = self.threat_search(board, size, in_a_row, -self.player, moves)
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
        
    def heuristic_eval(self, board, size, player):
        # Return some value that reprsents a 'good' guess of the value of the current position

        # Current version only checks values for the given player
        val = 0
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

    def get_valid_moves(self, board, size):
        moves = []
        mods = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1,), (1, -1), (-1, 1), (-1, -1))
        for i in range(size):
            for j in range(size):
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
                l, k1, k2 = 0, 1, 1
                while 0 <= x + k1*d[0] < size and 0 <= y + k1*d[1] < size and board[size*(x + k1*d[0]) + y + k1*d[1]] == player:
                    k1 += 1
                    l += 1
                while 0 <= x - k2*d[0] < size and 0 <= y - k2*d[1] < size and board[size*(x - k2*d[0]) + y - k2*d[1]] == player:
                    k2 += 1
                    l += 1
                # open
                if (k2 == 0 and 0 <= x + k1*d[0] < size and 0 <= y + k1*d[1] < size and board[size*(x + k1*d[0]) + y + k1*d[1]] == 0) or \
                   (k1 == 0 and 0 <= x - k1*d[0] < size and 0 <= y - k2*d[1] < size and board[size*(x - k2*d[0]) + y + k2*d[1]] == 0):
                    threats[i][0] += l**4                 
                # gaping
                elif k1 > 0 and k2 > 0 and 0 <= x + k1*d[0] < size and 0 <= y + k1*d[1] < size and 0 <= x - k2*d[0] < size and 0 <= y - k2*d[1] < size and \
                     board[size*(x + k1*d[0]) + y + k1*d[1]] == 0 and board[size*(x - k2*d[0]) + y - k2*d[1]] == 0:
                    threats[i][0] += l**4

                # gaping closed 
                #elif (k2 == 0 and 0 <= x + k1*d[0] < size and (0 <= y + k1*d[1] < size or board[size*(x + k1*d[0]) + y + k1*d[1]] == -player)):

                # closed
                elif (k2 == 0 and (x + k1*d[0] >= size or x + k1*d[0] < 0 or y + k1*d[1] >= size or y + k1*d[1] < 0 or board[size*(x + k1*d[0]) + y + k1*d[1]] == -player)) or \
                     (k1 == 0 and (x - k2*d[0] >= size or x - k2*d[0] < 0 or y - k2*d[1] >= size or y - k2*d[1] < 0 or board[size*(x - k2*d[0]) + y - k2*d[1]] == -player)):
                    threats[i][0] += l

                # Sort moves and retun top 
                threats = sorted(threats)[::-1]
                #print(threats)
                return [m for s, m in threats[:len(threats)//4 + 1]]

    def threat_space_shape_search(self, board, size, in_a_row, player, moves):
        for i in range(len(moves)):
            x, y = moves[i]
            



if __name__ == '__main__':
    size = 10
    in_a_row = 5
    max_depth = 9
    radius = 1

    game = Gomoku(size, in_a_row)
    agent1 = Agent(1, max_depth, radius, game)
    agent2 = Agent(-1, max_depth, radius, game)

    game.board[size*size//2 + size//2] = 1
    move2 = agent2.get_best_move(game.board, game.size, game.in_a_row)
    game.make_move(game.board, game.size, move2, -1)
    game.display_board(game.board, game.size)

    while True:
        print("Player 1")
        move1 = agent1.get_best_move(game.board, game.size, game.in_a_row)
        game.make_move(game.board, game.size, move1, 1)
        game.display_board(game.board, game.size)
        if game.is_winning_move(game.board, game.size, game.in_a_row, 1, move1):
            print("player1 wins")
            break
        
        print("Player 2")
        move2 = agent2.get_best_move(game.board, game.size, game.in_a_row)
        game.make_move(game.board, game.size, move2, -1)
        game.display_board(game.board, game.size)
        if game.is_winning_move(game.board, game.size, game.in_a_row, -1, move2):
            print("player2 wins")
            break



























































