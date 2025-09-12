#!/usr/bin/env python3
"""
Puzzle generator for Lime Sudoku puzzles.

"""

import argparse
import importlib
import time
# from solve_OR import solve as solve_OR # use this for initializing random answers
from puzzle_record import PuzzleRecord
from layout_classic import Layout as ClassicLayout
from layout_jiggy9 import Layout as JiggyLayout
from draw_limesudoku import draw_puzzle

parser = argparse.ArgumentParser(description='Generate Lime Sudoku puzzles')
parser.add_argument('-n', '--number', type=int, default=1,
                    help='Number of puzzles to generate (default: %(default)s)')
parser.add_argument('-r', '--random-seed', type=int, default=0,
                    help='Random seed (default: %(default)s)')
parser.add_argument('-z', '--allow_zeros', action='store_true',
                    help='Allow zero clues (default: False)')
# INSERT_YOUR_CODE
parser.add_argument('-dc', '--draw_candidates', action='store_true',
                    help='Draw candidate puzzles as images during generation (default: False)')
parser.add_argument('-s', '--solver', type=str, default='PR', choices=['OR', 'PR'], help='Solver to use (%(choices)s) (default: %(default)s)')
parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
parser.add_argument('-vv', '--very_verbose', action='store_true', help='Very verbose output')
parser.add_argument('-ed', '--even_distribute', action='store_true', default=False, help='Evenly distribute difficulties')
parser.add_argument('-maxt', '--max_tier', type=int, default=3,
                    help='Maximum tier of rules to use in the solver (default: no limit)')
parser.add_argument('-mint', '--min_tier', type=int, default=1,
                    help='Minimum tier of puzzles to produce (default: no minimum)')
parser.add_argument('-maxc', '--max_clues', type=int, default=15,
                    help='Maximum number of clues allowed in generated puzzles (no default)')
parser.add_argument('-rp', '--reduction_passes', type=int, default=3,
                    help='Number of reduction passes during puzzle refinement (default: %(default)s)')
parser.add_argument('-o', '--output_file', type=str,
                    help='Output file to write puzzles to (default: stdout)')
parser.add_argument('-sort', '--sort_by', type=str,
                    help='Sort puzzles by (none, clues, tier, work, branches)')
# parser.add_argument('-l', '--layout', default="classic", type=str)
parser.add_argument('-pt', '--puzzle_type', default="lime", type=str, 
                    help="Type of puzzle to generate (strings include lime, diagonals, windows, centerdot and jigsaw)")


args = parser.parse_args()

if args.very_verbose:
    args.verbose = True

if args.sort_by is None:
    args.sort_by = 'none' if args.solver == 'OR' else 'work'

solver_module = importlib.import_module(f'solve_{args.solver}')
solve = solver_module.solve

layout_module = JiggyLayout if 'jig' in args.puzzle_type else ClassicLayout

def refine_puzzle(puzzle_rec):
    """
    Refine the puzzle by removing unnecessary clues through 3 refinement passes.
    
    Args:
        fully_clued_puzzle: 81-character string with all clues
        
    Returns:
        Refined puzzle string with minimal necessary clues
    """
    import random
    
    best_puzzle = puzzle_rec.clone()
    min_clues = sum(1 for c in puzzle_rec.clues_string if c != '.')

    for pass_num in range(args.reduction_passes):
        # Start with the fully clued puzzle
        current_puzzle = puzzle_rec.clone()
        last_stats = None
        
        # Create shuffled list of all positions
        positions = list(range(81))
        random.shuffle(positions)
        
        # Try removing each clue one by one
        for pos in positions:
            test_puzzle = current_puzzle.clone()
            if test_puzzle.clues_string[pos] == '.':
                continue  # Skip positions that are already empty
                
            # Remove the clue
            test_puzzle.change_clue(pos, '.')
            
            # Test if the puzzle is still solvable, and save it, if so
            if args.very_verbose:
                print('solving ',test_puzzle.clues_string)
            result,stats = solve(test_puzzle, options={'max_tier':args.max_tier, 'verbose': args.verbose, 'very_verbose': args.very_verbose})

            if len(result) == 81:
                current_puzzle = test_puzzle
        
        # Count remaining clues
        remaining_clues = sum(1 for c in current_puzzle.clues_string if c != '.')
        
        # Keep the puzzle with the fewest clues
        if remaining_clues < min_clues:
            min_clues = remaining_clues
            best_puzzle = current_puzzle.clone()
            # best_puzzle.annotations = last_stats
            # best_stats = last_stats

    # print("best puzzle solution", best_puzzle.solution)
    
    return best_puzzle, best_puzzle.annotations


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
    layout = None

    dist_ctr = 0
    tier_distributoins = []
    if args.even_distribute:
        tier_distributions = list(range(args.min_tier, args.max_tier+1))
        args.min_tier = tier_distributions[0]
        args.max_tier = tier_distributions[0]
    
    tries = 0
    while len(puzzles) < n_puzzles:

        if layout == None or 'jig' in args.puzzle_type:
            # create a new layout
            if args.verbose:
                print(F"creating new layout")
            # layout_module = random.choice(layout_modules)
            layout = layout_module(9, args.puzzle_type)

        puzzle_rec = PuzzleRecord.generate_candidate_puzzle(layout, args.puzzle_type, f"puzzle-{len(puzzles)+1}", allow_zeros=allow_zeros)
        if puzzle_rec == None:
            # likely a bad layout, try again
            if args.verbose:
                print("bad layout, skipping")
            tries += 1
            continue

        if args.draw_candidates:
            draw_puzzle(f"drawings/candidate_{len(puzzles)+1}.png", puzzle_rec)
        
        if puzzle_rec is None:
            tries += 1
            continue
        
        # Refine puzzle
        refined,stats = refine_puzzle(puzzle_rec)

        if args.very_verbose:
            print(f"refined: {refined} {stats}")

        if args.min_tier is not None:
            tier_val = stats['mta'] if 'mta' in stats else stats.get('branches', 0)
            if tier_val < args.min_tier:
                if args.verbose:
                    print(f"Puzzle's tier {tier_val} < {args.min_tier} ")
                tries += 1
                continue

        if args.max_clues is not None:
            if sum([1 for c in refined.clues_string if c != '.']) > args.max_clues:
                if args.verbose:
                    print(f"Puzzle has {sum([1 for c in refined.clues_string if c != '.'])} clues > {args.max_clues}")
                tries += 1
                continue

        # if puzzle has any of (diagonals, windows, centerdot), insure puzzle is solveable by OR solver without that stuff
        if 'diagonals' in args.puzzle_type or 'windows' in args.puzzle_type or 'centerdot' in args.puzzle_type:
            puzzle_copy = refined.clone()
            layout_copy = puzzle_copy.layout.copy()
            layout_copy.containers = layout_copy.containers[:27] # remove diagonals, windows, centerdot
            puzzle_copy.layout = layout_copy
            result2,stats2 = solve(puzzle_copy)
            if len(result2) == 81:
                if args.verbose:
                    print(f"Puzzle extra containers can be ignored, skipping")
                tries += 1
                continue

        if not args.output_file: # output puzzle as generated
            print(str(refined))
        
        puzzles.append((refined, refined.solution, stats))
        tries += 1
        if args.even_distribute:
            dist_ctr += 1
            dist_ctr %= len(tier_distributions)
            args.min_tier = tier_distributions[dist_ctr]
            args.max_tier = tier_distributions[dist_ctr]

    if args.verbose:
        print("Tries", tries)
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
    total_clues += sum([1 for c in puzzle.clues_string if c != '.'])

import sys
cmdline_str = ' '.join(sys.argv)

if args.output_file:
    with open(args.output_file, 'w') as f:
        f.write(f"\n# Generated {args.number} puzzle(s) in {elapsed_time:.2f} seconds | {total_clues/args.number:.2f} avg clues/puzzle\n")
        f.write(f"\n# Command line: python {cmdline_str}\n")
        for pi,(puzzle,answer,stats) in enumerate(puzzles, 1):
            f.write(str(puzzle)+"\n")
else:
    print(f"\n# Generated {args.number} puzzle(s) in {elapsed_time:.2f} seconds | {total_clues/args.number:.2f} avg clues/puzzle")
    print(f"\n# Command line: python {cmdline_str}")


