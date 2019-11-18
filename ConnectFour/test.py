import numpy as np

n = 6
zeros = np.zeros([n, n])
for i in range(n):
    zeros[i][i] = 1

print(zeros[2:n+6, 2:n+6])