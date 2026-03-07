#!/usr/bin/env python3
from ortools.sat.python import cp_model

def convert_string_to_address(string):
    col = string[0]
    row = string[1]
    return int(row) - 1, ord(col) - ord('A')

def solve(puzzle_string, spairs, dpairs):
    """
    Solve a Classic Sudoku puzzle using OR-Tools SAT solver.
    
    Args:
        puzzle_string: 81-character string representing the puzzle
                      (dots for empty cells, numbers for clues)
    
    Returns:
        Either a solved puzzle string (with 'O' for limes) or "no solution"
        This example does not detect multiple solutions.
    """
    if len(puzzle_string) != 81:
        return "no solution"
    
    # Create the model
    model = cp_model.CpModel()

    
    # Create boolean variables for each cell (1 = mine, 0 = no mine)
    board = {}
    for row in range(9):
        for col in range(9):
            board[row, col] = model.NewIntVar(1,9,'mine_{row}_{col}')
    
    # Constraint 1: Each row must have different numbers (1-9)
    for row in range(9):
        row_cells = [board[row, col] for col in range(9)]
        model.AddAllDifferent(row_cells)
    
    # Constraint 2: Each column must have different numbers (1-9)
    for col in range(9):
        col_cells = [board[row, col] for row in range(9)]
        model.AddAllDifferent(col_cells)
    
    # Constraint 3: Each 3x3 block must have different numbers (1-9)
    for i in range(3):
        for j in range(3):
            block_cells = []
            for di in range(3):
                for dj in range(3):
                    block_cells.append(board[i * 3 + di, j * 3 + dj])
            model.AddAllDifferent(block_cells)
    
    # Constraint 4: Clue constraints - adjacent mine counts must match clues
    addr = 0
    for row in range(9):
        for col in range(9):
            if puzzle_string[addr] != '.':
                model.Add(board[row, col] == int(puzzle_string[addr]))
            addr += 1

    for a,b in spairs:
        arow,acol = convert_string_to_address(a)
        brow,bcol = convert_string_to_address(b)
        
        # Create an intermediate variable for the absolute difference
        diff = model.NewIntVar(-8, 8, f'diff_{a}_{b}')  # max range for 1-9 values
        abs_diff = model.NewIntVar(0, 8, f'abs_diff_{a}_{b}')
        
        # diff = board[arow, acol] - board[brow, bcol]
        model.Add(diff == board[arow, acol] - board[brow, bcol])
        # abs_diff = |diff|
        model.AddAbsEquality(abs_diff, diff)
        # abs_diff == 1
        model.Add(abs_diff == 1)

    for a,b in dpairs:
        arow,acol = convert_string_to_address(a)
        brow,bcol = convert_string_to_address(b)
        
        # Constrain such that |board[arow, acol] - board[brow, bcol]| == 2
        # Using boolean variables with OnlyEnforceIf for the OR constraint
        b1 = model.NewBoolVar(f'abs_diff2_case1_{a}_{b}')  # Case: a - b == 2
        b2 = model.NewBoolVar(f'abs_diff2_case2_{a}_{b}')  # Case: b - a == 2
        
        # If b1 is true, then a - b == 2
        model.Add(board[arow, acol] - board[brow, bcol] == 2).OnlyEnforceIf(b1)
        # If b2 is true, then b - a == 2
        model.Add(board[brow, bcol] - board[arow, acol] == 2).OnlyEnforceIf(b2)
        # At least one of the cases must be true
        model.AddBoolOr([b1, b2])

    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.INFEASIBLE:
        return "no solution"
    elif status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        
        # note: multiple solutions may exist!

        # retrieve current solution
        sol_str = ''
        for addr in range(81):
            sol_str += str(solver.Value(board[addr//9, addr%9]))
        return sol_str
    else:
        return "no solution"

def main():
    """Test the solver with the sample puzzle."""

    single_pairs = [('C1','D2'),('D1','C2'),('D1','E2'),('E1','F2'),('F1','G2'),('G1','H2'),
                    ('E2','D3'),('F2','G3'),('G2','H3'),('H2','G3'),
                    ('B3','C4'),('C3','B4'),('H3','I4'),
                    ('C4','D5'),('F4','E5'),('H4','G5'),
                    ('B5','A6'),
                    ('E6','F7'),('F6','G7'),
                    ('B7','C8'),('E7','F8'),('H7','I8'),
                    ('A8','B9'),('B8','A9'),('C8','D9'),('D8','E9'),('E8','F9'),('G8','H9'),('H8','I9')]
    double_pairs = [('B1','A2'),('H1','I2'),
                    ('B2','A3'),('I2','H3'),
                    ('B4','C5'),
                    ('C5','D6'),('F5','G6'),
                    ('A7','B8'),('B8','C9')]

    puzzle = ['.'] * 81

    print(f"Solving puzzle with OR-Tools SAT solver...")
    result = solve(puzzle, single_pairs, double_pairs)
    print(f"Result  : {result}")

if __name__ == "__main__":
    main() 

