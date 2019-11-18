import numpy as np
import time as time


class Gomoku:

    def __init__(self, size, in_a_row):
        self.size = size
        self.in_a_row = in_a_row
        self.board = np.zeros([size, size]).flatten()

    def is_winning_move(self, board, size, in_a_row, player, move):
        x, y = move
        # ROW
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
        if board[size*move[0] + move[1]] == 0:
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
        self.threat_scores = self.generate_threat_scores()

    def generate_threat_scores(self):
        scores = {}
        for i in range(self.game.in_a_row):
            #open
            print(0)
            #close

    def get_best_move(self, board, size, in_a_row):
        self.hash_table = {}
        return self.maxi(board, size, in_a_row, 0, float('-inf'), float('inf'), (-1, -1))    

    def maxi(self, board, size, in_a_row, depth, alpha, beta, last_move):
        #print('maxi', depth, alpha, beta, last_move)
        #self.game.display_board(board, size)
        #print(board)
        #print("####################")
        #time.sleep(1.5)
        
        # Gets actual move on the AIs first call of this function
        if depth == 0:
            moves = self.get_valid_moves(board, size)
            scores = sorted([
                (self.mini(board, size, in_a_row, depth + 1, alpha, beta, move), move) for move in moves
                ])[::-1]
            for score in scores:
                print(score)
            return scores[0][1]
        # MAKE MOVE
        board[size*last_move[0] + last_move[1]] = -self.player
        if tuple(board) in self.hash_table:
            val = self.hash_table[tuple(board)]
            board[size*last_move[0] + last_move[1]] = 0
            return val
        if self.game.is_winning_move(board, size, in_a_row, -self.player, last_move):
            self.hash_table[tuple(board)] = -self.M + depth
            #self.game.display_board(board, size)
            board[size*last_move[0] + last_move[1]] = 0
            return -self.M + depth
        if depth == self.max_depth:
            val = -self.heuristic_eval(board, size, -self.player)
            self.hash_table[tuple(board)] = val
            board[size*last_move[0] + last_move[1]] = 0
            return val
        moves = self.get_valid_moves(board, size)
        if moves == []:
            return 0
        else:
            moves = self.threat_search(board, size, in_a_row, self.player, moves)
        best_val = float('-inf')
        for move in moves:
            val = self.mini(board, size, in_a_row, depth + 1, alpha, beta, move)
            best_val = max(val, best_val)
            alpha = max(alpha, best_val)
            if alpha >= beta:
                #print('maxi', alpha, beta)
                break
        self.hash_table[tuple(board)] = best_val
        board[size*last_move[0] + last_move[1]] = 0
        return best_val

    def mini(self, board, size, in_a_row, depth, alpha, beta, last_move):
        #print('Mini', depth, alpha, beta, last_move)
        #self.game.display_board(board, size)
        #print(board)
        #print("######################")
        #time.sleep(1.5)
        
        # Make move
        board[size*last_move[0] + last_move[1]] = self.player
        # Already seen position
        if tuple(board) in self.hash_table:
            val = self.hash_table[tuple(board)]
            board[size*last_move[0] + last_move[1]] = 0
            return val
        # Game over
        if self.game.is_winning_move(board, size, in_a_row, self.player, last_move):
            self.hash_table[tuple(board)] = self.M - depth
            board[size*last_move[0] + last_move[1]] = 0
            return self.M - depth
        # No more searching
        if depth == self.max_depth:
            val = self.heuristic_eval(board, size, self.player)
            self.hash_table[tuple(board)] = val
            board[size*last_move[0] + last_move[1]] = 0
            return val
        best_val = float('inf')
        moves = self.get_valid_moves(board, size)
        if moves == []:
            return 0
        else:
            moves = self.threat_search(board, size, in_a_row, -self.player, moves)
        for move in moves:
            val = self.maxi(board, size, in_a_row, depth + 1, alpha, beta, move)
            best_val = min(val, best_val)
            beta = min(best_val, beta)
            if alpha >= beta:
                #print('mini',  alpha, beta)
                break
        self.hash_table[tuple(board)] = best_val
        board[size*last_move[0] + last_move[1]] = 0
        return best_val
        
    def heuristic_eval(self, board, size, player):
        val = 0
        for i in range(size):
            for j in range(size):
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



























































