#!/usr/bin/env python3
"""
Puzzle generator for Lime Sudoku puzzles.
"""

import argparse
from solve_OR import solve


def generate_candidate_answer(rand_seed=0):
    """
    Generate a random answer string using the method from test_random.py.
    
    Args:
        rand_seed: Random seed for reproducibility
        
    Returns:
        81-character string with 'O' for mines and '.' for empty cells
    """
    # Use the solve function with an empty puzzle and specific random seed
    # This generates a random valid solution
    return solve('.' * 81, rand_seed=rand_seed, max_solutions=1)


def generate_fully_clued_puzzle(answer_string):
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
    
    return ''.join(clued_puzzle)


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
    
    for pass_num in range(3):
        # Start with the fully clued puzzle
        current_puzzle = list(fully_clued_puzzle)
        
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
            result = solve(test_puzzle)
            
            # If not solvable (result is not 81 chars), restore the clue
            if len(result) != 81:
                current_puzzle[pos] = original_clue
        
        # Count remaining clues
        remaining_clues = sum(1 for c in current_puzzle if c != '.')
        
        # Keep the puzzle with the fewest clues
        if remaining_clues < min_clues:
            min_clues = remaining_clues
            best_puzzle = ''.join(current_puzzle)
    
    return best_puzzle


def generate_puzzles(n_puzzles=1, rand_seed=0):
    """
    Generate puzzles using the specified pipeline.
    
    Args:
        n_puzzles: Number of puzzles to generate
        rand_seed: Base random seed (will be incremented for each puzzle)
        
    Returns:
        List of puzzle strings
    """
    puzzles = []
    
    for i in range(n_puzzles):
        # Generate candidate answer
        answer = generate_candidate_answer(rand_seed + i)
        
        # Generate fully clued puzzle
        fully_clued = generate_fully_clued_puzzle(answer)
        
        # Refine puzzle
        refined = refine_puzzle(fully_clued)
        
        puzzles.append(refined)
    
    return puzzles


def main():
    """Main function to handle command line arguments and generate puzzles."""
    import time
    
    parser = argparse.ArgumentParser(description='Generate Lime Sudoku puzzles')
    parser.add_argument('-n', '--number', type=int, default=1,
                       help='Number of puzzles to generate (default: 1)')
    parser.add_argument('-r', '--random-seed', type=int, default=0,
                       help='Random seed (default: 0)')
    
    args = parser.parse_args()

    # seed the random number generator here
    import random
    random.seed(args.random_seed)
    
    # Start timing
    start_time = time.time()
    
    # Generate puzzles
    puzzles = generate_puzzles(args.number, args.random_seed)
    
    # Output puzzles, one per line
    for puzzle in puzzles:
        print(puzzle)
    
    # Report elapsed time
    elapsed_time = time.time() - start_time
    print(f"\n# Generated {args.number} puzzle(s) in {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main() 