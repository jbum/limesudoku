#!/usr/bin/env python3
"""
Puzzle generator for Lime Sudoku puzzles.

"""

import argparse
import importlib
import time
from solve_OR import solve as solve_OR # use this for initializing random answers

parser = argparse.ArgumentParser(description='Generate Lime Sudoku puzzles')
parser.add_argument('-n', '--number', type=int, default=1,
                    help='Number of puzzles to generate (default: %(default)s)')
parser.add_argument('-r', '--random-seed', type=int, default=0,
                    help='Random seed (default: %(default)s)')
parser.add_argument('-z', '--allow_zeros', action='store_true',
                    help='Allow zero clues (default: False)')
parser.add_argument('-s', '--solver', type=str, default='PR', choices=['OR', 'PR'], help='Solver to use (%(choices)s) (default: %(default)s)')
parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
parser.add_argument('-vv', '--very_verbose', action='store_true', help='Very verbose output')
parser.add_argument('-maxt', '--max_tier', type=int, 
                    help='Maximum tier of rules to use in the solver (default: no limit)')
parser.add_argument('-mint', '--min_tier', type=int,
                    help='Minimum tier of puzzles to produce (default: no minimum)')
parser.add_argument('-maxc', '--max_clues', type=int, default=15,
                    help='Maximum number of clues allowed in generated puzzles (no default)')
parser.add_argument('-rp', '--reduction_passes', type=int, default=3,
                    help='Number of reduction passes during puzzle refinement (default: %(default)s)')
parser.add_argument('-o', '--output_file', type=str,
                    help='Output file to write puzzles to (default: stdout)')
parser.add_argument('-sort', '--sort_by', type=str,
                    help='Sort puzzles by (none, clues, tier, work, branches)')


args = parser.parse_args()

if args.very_verbose:
    args.verbose = True

if args.sort_by is None:
    args.sort_by = 'none' if args.solver == 'OR' else 'work'

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
    for pass_num in range(args.reduction_passes):
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
    
    tries = 0
    while len(puzzles) < n_puzzles:
        # Generate candidate answer
        answer = generate_candidate_answer(rand_seed + tries)
        
        # Generate fully clued puzzle - this may fail if we can't solve it without zeros
        fully_clued = generate_fully_clued_puzzle(answer, allow_zeros)
        
        if fully_clued is None:
            tries += 1
            continue  # Try again with next seed
        
        # Refine puzzle
        refined,stats = refine_puzzle(fully_clued)

        if args.min_tier is not None:
            tier_val = stats['mta'] if 'mta' in stats else stats.get('branches', 0)
            if tier_val < args.min_tier:
                tries += 1
                continue

        if args.max_clues is not None:
            if sum([1 for c in refined if c != '.']) > args.max_clues:
                tries += 1
                continue

        if not args.output_file: # output puzzle as generated
            print(f"puzzle-{tries+1}\tlime\t{refined}\t{answer}\t{stats}")
        
        puzzles.append((refined, answer, stats))
        tries += 1
    
    return puzzles


# seed the random number generator here
import random
random.seed(args.random_seed)

# Start timing
start_time = time.time()

# Generate puzzles
puzzles = generate_puzzles(args)

elapsed_time = time.time() - start_time

# Output puzzles, one per line
total_clues = 0
# Sort puzzles according to the key specified in args.sort_by (default: 'work')
sort_key = args.sort_by
if sort_key != 'none':
    def get_sort_val(puz_tuple):
        stats = puz_tuple[2]
        # Try to get the sort key from stats, fallback to 0 if not present
        return stats.get(sort_key, 0)
    puzzles.sort(key=get_sort_val)

# count total clues in separate loop
for pi,(puzzle,answer,stats) in enumerate(puzzles, 1):
    total_clues += sum([1 for c in puzzle if c != '.'])

import sys
cmdline_str = ' '.join(sys.argv)

if args.output_file:
    with open(args.output_file, 'w') as f:
        f.write(f"\n# Generated {args.number} puzzle(s) in {elapsed_time:.2f} seconds | {total_clues/args.number:.2f} avg clues/puzzle\n")
        f.write(f"\n# Command line: python {cmdline_str}\n")
        for pi,(puzzle,answer,stats) in enumerate(puzzles, 1):
            f.write(f"puzzle-{pi}\tlime\t{puzzle}\t{answer}\t{stats}\n")
else:
    print(f"\n# Generated {args.number} puzzle(s) in {elapsed_time:.2f} seconds | {total_clues/args.number:.2f} avg clues/puzzle")
    print(f"\n# Command line: python {cmdline_str}")


