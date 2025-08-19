#!/usr/bin/env python3
#
# mostly the work of claude-opus-4
# jbum added timing and solution counting

import sys
import time
import argparse
from draw_limesudoku import draw_puzzle
import importlib

parser = argparse.ArgumentParser(description='Solve puzzles from a test suite file.')
parser.add_argument('filename', type=str, help='Path to the test suite file')
parser.add_argument('--rand_seed', type=int, default=None, help='Random seed for the solver')
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
parser.add_argument('-vv', '--very_verbose', action='store_true', help='Enable very verbose output (implies --verbose)')
parser.add_argument('-ofst', '--puzzle_offset', type=int, default=1, help='Index of first puzzle to solve (1-based)')
parser.add_argument('-n', '--number_to_solve', type=int, default=None, help='Number of puzzles to solve (default: all)')
parser.add_argument('-abc', '--average_branch_count', action='store_true', help='Show average branch count statistics')
parser.add_argument('-dp', '--draw_puzzle', action='store_true', help='Draw the puzzle')
parser.add_argument('-s', '--solver', type=str, default='OR', help='Solver to use (OR, PR)')

args = parser.parse_args()
if args.very_verbose:
    args.verbose = True

solver_module = importlib.import_module(f'solve_{args.solver}')
solve = solver_module.solve

def read_puzzles_from_file(filename):
    """
    Read puzzles from a test suite file.
    
    Args:
        filename: Path to the test suite file
    
    Returns:
        List of tuples (puzzle_string, comment)
    """
    puzzles = []
    
    try:
        with open(filename, 'r') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                
                # Skip empty lines and comment-only lines
                if not line or line.startswith('#'):
                    continue
                
                # Split on '#' to separate puzzle from comment
                parts = line.split('#', 1)
                puzzle_str = parts[0].strip()
                comment = parts[1].strip() if len(parts) > 1 else ""
                
                # Validate puzzle string length (should be 81 characters)
                if len(puzzle_str) != 81:
                    print(f"Warning: Line {line_num} has invalid puzzle length {len(puzzle_str)}, skipping")
                    continue
                
                # Validate puzzle string contains only valid characters
                valid_chars = set('.012345678')
                if not all(c in valid_chars for c in puzzle_str):
                    print(f"Warning: Line {line_num} contains invalid characters, skipping")
                    continue
                
                puzzles.append((puzzle_str, comment))
                
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        return []
    except Exception as e:
        print(f"Error reading file '{filename}': {e}")
        return []
    
    return puzzles

def solve_puzzles_from_file(filename):
    """
    Solve all puzzles from a test suite file.
    
    Args:
        filename: Path to the test suite file
    """
    puzzles = read_puzzles_from_file(filename)
    
    if not puzzles:
        print("No valid puzzles found in the file.")
        return
    
    if args.verbose:
        print(f"Found {len(puzzles)} puzzles to solve.\n")
    nbr_solved = 0

    start_time = time.perf_counter()
    for i, (puzzle_str, comment) in enumerate(puzzles, 1):
        if args.verbose:
            print(f"Puzzle {i}:")
            print(f"  Puzzle: {puzzle_str}")
            if comment:
                print(f"  Comment: {comment}")

        if i < args.puzzle_offset:
            continue
        
        answer,stats = solve(puzzle_str)
        if len(answer) == 81:
            nbr_solved += 1

            if args.average_branch_count:
                tot_solved = 1
                tot_branch_count = stats['branches']
                for r in range(1,5):
                    _,stats = solve(puzzle_str, rand_seed=r)
                    tot_solved += 1
                    tot_branch_count += stats['branches']
                avg_branch_count = tot_branch_count / tot_solved
                print(f"{puzzle_str}\t# {answer} #{i:<3d} abc={avg_branch_count:.1f}")

            if args.draw_puzzle:
                draw_puzzle(f"drawings/puzzle_{i}.svg", puzzle_str, None, annotation=f"Puzzle #{i}")

        if args.verbose:
            print(f"  Result: {answer}")
            print()

        if args.number_to_solve and nbr_solved >= args.number_to_solve:
            break

    end_time = time.perf_counter()
    elapsed_microseconds = int((end_time - start_time) * 1_000_000)
    print(f"# {nbr_solved}/{len(puzzles)} puzzles solved in {elapsed_microseconds} microseconds.")



solve_puzzles_from_file(args.filename)
