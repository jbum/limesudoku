#!/usr/bin/env python3
from ortools.sat.python import cp_model
import time

# jbum added this class to get callback for each solution, and quit when 2 solutions are found
class MySolutionChecker(cp_model.CpSolverSolutionCallback):
    def __init__(self, flat_board, max_solutions = 2):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._board = flat_board
        self._solution_set = set()
        self._SOL_LIMIT = max_solutions

    def on_solution_callback(self):
        sol_list = (tuple([self.Value(p) for p in self._board]))
        self._solution_set.add(sol_list)
        if len(self._solution_set) >= self._SOL_LIMIT:
            self.stop_search()
  
    def solution_count(self):
        return len(self._solution_set)
    
    def solution_set(self):
        return list(self._solution_set)

def get_adjacent_positions(row, col):
    """Get all adjacent positions (including diagonally) for a cell."""
    positions = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = row + dr, col + dc
            if 0 <= nr < 9 and 0 <= nc < 9:
                positions.append((nr, nc))
    return positions

def vals_to_string(sol):
    """Convert 2D grid to string representation."""
    return ''.join(['.' if sol[_] == 0 else 'O' for _ in range(81)])

def solve(puzzle_string, rand_seed = int(time.time()), max_solutions = 2):
    """
    Solve a Lime Sudoku puzzle using OR-Tools SAT solver.
    
    Args:
        puzzle_string: 81-character string representing the puzzle
                      (dots for empty cells, numbers for clues)
    
    Returns:
        Either a solved puzzle string (with 'O' for limes) or
        "no solution" or "multiple solutions"
    """
    if len(puzzle_string) != 81:
        return "no solution"
    
    # Create the model
    model = cp_model.CpModel()
    
    # Create boolean variables for each cell (1 = mine, 0 = no mine)
    mines = {}
    flat_board = []
    for row in range(9):
        for col in range(9):
            mines[row, col] = model.NewBoolVar(f'mine_{row}_{col}')
            flat_board.append(mines[row, col])
    
    # Constraint 1: Each row must have exactly 3 mines
    for row in range(9):
        row_mines = [mines[row, col] for col in range(9)]
        model.Add(sum(row_mines) == 3)
    
    # Constraint 2: Each column must have exactly 3 mines
    for col in range(9):
        col_mines = [mines[row, col] for row in range(9)]
        model.Add(sum(col_mines) == 3)
    
    # Constraint 3: Each 3x3 block must have exactly 3 mines
    for block_row in range(0, 9, 3):
        for block_col in range(0, 9, 3):
            block_mines = []
            for r in range(block_row, block_row + 3):
                for c in range(block_col, block_col + 3):
                    block_mines.append(mines[r, c])
            model.Add(sum(block_mines) == 3)
    
    # Constraint 4: Clue constraints - adjacent mine counts must match clues
    addr = 0
    for row in range(9):
        for col in range(9):
            if puzzle_string[addr] in '012345678':
                expected_count = int(puzzle_string[addr])
                adjacent_mines = []
                
                # Get all adjacent positions
                for adj_row, adj_col in get_adjacent_positions(row, col):
                    adjacent_mines.append(mines[adj_row, adj_col])
                
                # Add constraint that sum of adjacent mines equals the clue
                model.Add(sum(adjacent_mines) == expected_count)
                # jim - added this constraint to prevent solutions with mines on clued cells
                model.Add(mines[row, col] == 0)
            addr += 1
    
    # Solve the model
    solver = cp_model.CpSolver()
    solution_printer = MySolutionChecker(flat_board, max_solutions)
    solver.parameters.enumerate_all_solutions = True # this is hugely important

    solver.parameters.random_seed = rand_seed

    status = solver.Solve(model, solution_printer)

    if solution_printer.solution_count() == 0:
        return "no solution", None
    elif solution_printer.solution_count() > 1:
        return "multiple solutions", None
    return vals_to_string(solution_printer.solution_set()[0]), {'branches': solver.NumBranches()}


def main():
    """Test the solver with the sample puzzle."""
    sample_puzzle = ".21.......3.3...........3...34.....3...........4....4.2...3.4.................4.."
    print("Solving puzzle with OR-Tools SAT solver...", sample_puzzle)
    for r in range(1,5):
        result,stats = solve(sample_puzzle, rand_seed=r)
        print(f"Result: {result}", f"rand_seed: {r}",stats)

if __name__ == "__main__":
    main() 