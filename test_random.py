# test random

from solve_OR import solve
import time

for i in range(10):
    sol,stats = solve( '.' * 81 , rand_seed=i, max_solutions=1 )
    print(sol)


