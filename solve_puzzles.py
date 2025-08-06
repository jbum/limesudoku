#!/usr/bin/env python3
#
# mostly the work of claude-opus-4
# jbum added timing and solution counting

import sys
from solve_OR import solve
import time

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
    
    print(f"Found {len(puzzles)} puzzles to solve.\n")
    nbr_solved = 0

    start_time = time.perf_counter()
    for i, (puzzle_str, comment) in enumerate(puzzles, 1):
        print(f"Puzzle {i}:")
        print(f"  Puzzle: {puzzle_str}")
        if comment:
            print(f"  Comment: {comment}")
        
        result = solve(puzzle_str)
        if len(result) == 81:
            nbr_solved += 1
        print(f"  Result: {result}")
        print()
    end_time = time.perf_counter()
    elapsed_microseconds = int((end_time - start_time) * 1_000_000)
    print(f"Solving loop took {elapsed_microseconds} microseconds.")
    print(f"Solved {nbr_solved} puzzles.")

def main():
    """Main function to solve puzzles from a test suite file."""
    if len(sys.argv) != 2:
        print("Usage: python3 solve_puzzles.py <test_suite_file>")
        print("Example: python3 solve_puzzles.py testsuites/testsuite_1.txt")
        sys.exit(1)
    
    filename = sys.argv[1]
    solve_puzzles_from_file(filename)

if __name__ == "__main__":
    main() 