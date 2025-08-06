#!/usr/bin/env python3
from ortools.sat.python import cp_model

def solve(puzzle_string):
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
    tests = [{'puzzle': '....5....3.7..1.5.4..6.2..1...2..4.3.2.....9.8.3..4...2..8.3..5.3.5..9.7....4....', 'expected': '912357864367481259485692731591268473624735198873914526249873615138526947756149382'}, # tough
             {'puzzle': '1.6..85...9.6...23......1.75...7...6...4.9...3...2...19.1......27...4.3...39..7.8', 'expected': '126738594795641823834295167519873246682419375347526981961387452278154639453962718'},
             {'puzzle': '.2....79.....3..8...54.7..1.12.......4.851.7.......91.2..6.41...8..9.....53....4.', 'expected': '324518796167239485895467231712943568946851372538726914279684153481395627653172849'},
             {'puzzle': '...7.4......8..25.1.6.5......9.....3..24.58..6.....4......4.6.9.57..1......2.8...', 'expected': '528714936794836251136952784849127563312465897675389412281543679457691328963278145'}, # insane
             {'puzzle': '.8..7.1...714....56..8....345...36.............31...541....7..67....823...2.1..8.', 'expected': '984375162371462895625891473459723618817546329263189754198237546746958231532614987'},
             {'puzzle': '..8....65.3..9.....4.8.6..7.6...3....2..4..1....7...4.4..6.9.3.....1..5.21....8..', 'expected': '978421365632597481541836927864153279725948613193762548457689132389214756216375894'}]



    for test in tests:
        print(f"Solving puzzle with OR-Tools SAT solver...", test['puzzle'])
        result = solve(test['puzzle'])
        print(f"Puzzle  : {test['puzzle']}")
        print(f"Result  : {result}")
        if (result != test['expected']):
            print(f"Expected: {test['expected']}")
            print(f"Failed!")
        print()

if __name__ == "__main__":
    main() 

