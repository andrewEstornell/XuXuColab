import numpy as np
import gomoku as gk

game = gk.Gomoku(8, 5)
agent = gk.Agent(1, 7, 1, game)

board = [[0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 1, 1, 1, 0, 0, 0],
         [0, 0, 0, 0, 1, 0, 0, 0],
         [0, 0, 1, 0, 1, 0, 0, 0],
         [0, 0, 1, 0, 1, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0]]

board = np.array(board).flatten()
print(agent.threat_space_test(board, 8, 5, [(1, 4)]))