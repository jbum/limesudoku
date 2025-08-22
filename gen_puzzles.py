#!/usr/bin/env python3
"""
Puzzle generator for Lime Sudoku puzzles.

Generated mostly with Cursor/Claude

HISTORY:
8/5/2025
Prompts:
1. Make a new script for generating puzzles.  gen_puzzles.py. It'll use argparse to get some optional params -n <nbr_puzzles> and -r <random_seed>. Number puzzles defaults to 1, random seed defaults to 0.  It'll loop and produce each puzzle, one per line, using the format In my testsuites/sample_puzzles.tsv file.  The generate_puzzles function should call generate_candidate_answer, generate_fully_clued_puzzle, and refine_puzzle.  generate_candidate_answer, should use the method in test_random.py to generate a random answer string.  generate_fully_clued_puzzle will generate a string where each mine is a dot, and every other square is the number of adjacent mines.  Leave refine_puzzle blank for now and just have it return the fully-clued puzzle that is passed into it.  
2. Okay, the refine_puzzle will do three refinement_passes.  In each one, it will start with the fully-clued puzzle and remove clues, randomly (using a shuffled address list), one-at-a-time.  It will then call solve() on the modified puzzle, with no other arguments.  If the solver does not return an 81 character string, then it will restore the deleted clue, since it's necessary to solve the puzzle.  After going through all the clues, the remaining clues are necessary.  It will keep the puzzle with the fewest number of clues after the 3 passes, and return that.
3. In the main function please add some elapsed time measurement and report it at the end.
(Manually fixed issue with seeding random generator)
8/6/2025
(Added command line feedback comment using CMD-K)
(Manually fixed it to make zero-clues optional, default is no zeros)
8/7/2025
Added support for annotations in solver.  Reporting on OR-Tools branch count.  Regenerated test suites with this info.
8/19/2025
Added support for multiple solvers via --solver param.
Added preliminiary PR (production-rule) solver.
8/20/2025
Added --max-tier parameter to limit difficulty of output puzzles when used with PR solver.
Modified solvers to put most optional arguments in a dictionary.

"""

import argparse
import importlib
import time
from solve_OR import solve as solve_OR # use this for initializing random answers

parser = argparse.ArgumentParser(description='Generate Lime Sudoku puzzles')
parser.add_argument('-n', '--number', type=int, default=1,
                    help='Number of puzzles to generate (default: 1)')
parser.add_argument('-r', '--random-seed', type=int, default=0,
                    help='Random seed (default: 0)')
parser.add_argument('-z', '--allow_zeros', action='store_true',
                    help='Allow zero clues (default: False)')
parser.add_argument('-s', '--solver', type=str, default='OR', help='Solver to use (OR, PR)')
parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
parser.add_argument('-vv', '--very_verbose', action='store_true', help='Very verbose output')
parser.add_argument('-mt', '--max_tier', type=int, 
                    help='Maximum tier of rules to use in the solver (default: no limit)')

args = parser.parse_args()

if args.very_verbose:
    args.verbose = True

solver_module = importlib.import_module(f'solve_{args.solver}')
solve = solver_module.solve



def generate_candidate_answer(rand_seed=0):
    """
    Generate a random answer string using the method from test_random.py.
    
    Args:
        rand_seed: Random seed for reproducibility
        
    Returns:
        81-character string with 'O' for mines and '.' for empty cells
    """
    # Use the solve_OR function with an empty puzzle and specific random seed
    # This generates a random valid solution
    solution,_ = solve_OR('.' * 81, options={'rand_seed':rand_seed, 'max_solutions':1})
    return solution


def generate_fully_clued_puzzle(answer_string, allow_zeros=False):
    """
    Generate a fully clued puzzle from an answer string.
    
    Args:
        answer_string: 81-character string with 'O' for mines and '.' for empty cells
        
    Returns:
        81-character string where each mine is a dot, and every other square 
        is the number of adjacent mines
    """
    if len(answer_string) != 81:
        raise ValueError("Answer string must be 81 characters long")
    
    # Convert answer string to 2D grid for easier processing
    grid = []
    for i in range(9):
        row = []
        for j in range(9):
            idx = i * 9 + j
            row.append(1 if answer_string[idx] == 'O' else 0)
        grid.append(row)
    
    # Generate clued puzzle
    clued_puzzle = []
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 1:  # Mine
                clued_puzzle.append('.')
            else:  # Count adjacent mines
                count = 0
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        ni, nj = i + di, j + dj
                        if 0 <= ni < 9 and 0 <= nj < 9:
                            count += grid[ni][nj]
                clued_puzzle.append(str(count))

    puzzle_str = ''.join(clued_puzzle)
    if not allow_zeros:
        # remove the zeros
        puzzle_str = puzzle_str.replace('0', '.')
    # attempt to solve it, if we can't solve it return None
    result,_ = solve(puzzle_str, options={'max_tier':args.max_tier})
    if len(result) != 81:
        return None
    
    return puzzle_str


def refine_puzzle(fully_clued_puzzle):
    """
    Refine the puzzle by removing unnecessary clues through 3 refinement passes.
    
    Args:
        fully_clued_puzzle: 81-character string with all clues
        
    Returns:
        Refined puzzle string with minimal necessary clues
    """
    import random
    
    best_puzzle = fully_clued_puzzle
    min_clues = sum(1 for c in fully_clued_puzzle if c != '.')
    best_stats = None
    for pass_num in range(3):
        # Start with the fully clued puzzle
        current_puzzle = list(fully_clued_puzzle)
        last_stats = None
        
        # Create shuffled list of all positions
        positions = list(range(81))
        random.shuffle(positions)
        
        # Try removing each clue one by one
        for pos in positions:
            if current_puzzle[pos] == '.':
                continue  # Skip positions that are already empty
                
            # Store the original clue
            original_clue = current_puzzle[pos]
            
            # Remove the clue
            current_puzzle[pos] = '.'
            
            # Test if the puzzle is still solvable
            test_puzzle = ''.join(current_puzzle)
            result,stats = solve(test_puzzle, options={'max_tier':args.max_tier})

            # print("refine",result,stats)
            
            # If not solvable (result is not 81 chars), restore the clue
            if len(result) != 81:
                current_puzzle[pos] = original_clue
            else:
                last_stats = stats
        
        # Count remaining clues
        remaining_clues = sum(1 for c in current_puzzle if c != '.')
        
        # Keep the puzzle with the fewest clues
        if remaining_clues < min_clues:
            min_clues = remaining_clues
            best_puzzle = ''.join(current_puzzle)
            best_stats = last_stats
    
    return best_puzzle, best_stats


def generate_puzzles(args):
    """
    Generate puzzles using the specified pipeline.
    
    Args:
        n_puzzles: Number of puzzles to generate
        rand_seed: Base random seed (will be incremented for each puzzle)
        
    Returns:
        List of puzzle strings
    """
    n_puzzles = args.number
    rand_seed = args.random_seed
    allow_zeros = args.allow_zeros
    puzzles = []
    
    i = 0
    while len(puzzles) < n_puzzles:
        # Generate candidate answer
        answer = generate_candidate_answer(rand_seed + i)
        
        # Generate fully clued puzzle - this may fail if we can't solve it without zeros
        fully_clued = generate_fully_clued_puzzle(answer, allow_zeros)
        
        if fully_clued is None:
            i += 1
            continue  # Try again with next seed
        
        # Refine puzzle
        refined,stats = refine_puzzle(fully_clued)
        
        puzzles.append((refined, answer, stats))
        i += 1
    
    return puzzles


# seed the random number generator here
import random
random.seed(args.random_seed)

# Start timing
start_time = time.time()

# Generate puzzles
puzzles = generate_puzzles(args)

# Output puzzles, one per line
for puzzle,answer,stats in puzzles:
    print(f"{puzzle}\t# {answer}\t{stats}")

# Report elapsed time
elapsed_time = time.time() - start_time
print(f"\n# Generated {args.number} puzzle(s) in {elapsed_time:.2f} seconds")

# Construct a string from the command line arguments and print as a comment
import sys
cmdline_str = ' '.join(sys.argv)
print(f"# Command line: python {cmdline_str}")
