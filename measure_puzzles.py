#!/usr/bin/env python3
#
# measure_puzzles.py - Analyze puzzle statistics from a testsuite file
# Based on the file loading method from solve_puzzles.py

import sys
import argparse

def read_puzzles_from_file(filename):
    """
    Read puzzles from a test suite file.
    
    Args:
        filename: Path to the test suite file
    
    Returns:
        List of tuples (puzzle_string, answer_string, comment)

    History:
        This was made with Cursor, using the following prompts.
        1. Using a file loading and parsing method similar to the one used in solve_puzzles.py, 
        make a new script, measure_puzzles.py.  We give it a testsuite file, and it loads the]
        puzzles and prints stats.  Compute an average clue_count for the set of puzzles.  
        Also use a set() to check if there are any duplicate answers.

        I then commented out some parts of the report that aren't super interesting.

    """
    puzzles = []
    
    try:
        with open(filename, 'r') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                
                # Skip empty lines and comment-only lines
                if not line or line.startswith('#'):
                    continue
                
                # Split on '#' to separate puzzle from answer and comment
                parts = line.split('#', 2)
                puzzle_str = parts[0].strip()
                answer_str = parts[1].strip() if len(parts) > 1 else ""
                comment = parts[2].strip() if len(parts) > 2 else ""
                
                # Validate puzzle string length (should be 81 characters)
                if len(puzzle_str) != 81:
                    print(f"Warning: Line {line_num} has invalid puzzle length {len(puzzle_str)}, skipping")
                    continue
                
                # Validate puzzle string contains only valid characters
                valid_chars = set('.012345678')
                if not all(c in valid_chars for c in puzzle_str):
                    print(f"Warning: Line {line_num} contains invalid characters, skipping")
                    continue
                
                puzzles.append((puzzle_str, answer_str, comment))
                
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        return []
    except Exception as e:
        print(f"Error reading file '{filename}': {e}")
        return []
    
    return puzzles

def count_clues(puzzle_str):
    """Count the number of clues (non-dot characters) in a puzzle string."""
    return sum(1 for c in puzzle_str if c != '.')

def analyze_puzzles(filename):
    """Analyze puzzles from a testsuite file and print statistics."""
    puzzles = read_puzzles_from_file(filename)
    
    if not puzzles:
        print("No valid puzzles found in the file.")
        return
    
    print(f"Found {len(puzzles)} valid puzzles.\n")
    
    # Calculate clue counts and collect answers
    clue_counts = []
    answers = set()
    duplicate_answers = set()
    
    for i, (puzzle_str, answer_str, comment) in enumerate(puzzles, 1):
        clue_count = count_clues(puzzle_str)
        clue_counts.append(clue_count)
        
        # Check for duplicate answers
        if answer_str:
            if answer_str in answers:
                duplicate_answers.add(answer_str)
            else:
                answers.add(answer_str)
    
    # Calculate statistics
    total_clues = sum(clue_counts)
    avg_clue_count = total_clues / len(puzzles)
    min_clues = min(clue_counts)
    max_clues = max(clue_counts)
    
    # Print statistics
    print("=== PUZZLE STATISTICS ===")
    print(f"Total puzzles: {len(puzzles)}")
    print(f"Total clues: {total_clues}")
    print(f"Average clue count: {avg_clue_count:.2f}")
    print(f"Minimum clue count: {min_clues}")
    print(f"Maximum clue count: {max_clues}")
    print()
    
    # Clue count distribution
    clue_distribution = {}
    for count in clue_counts:
        clue_distribution[count] = clue_distribution.get(count, 0) + 1
    
    print("=== CLUE COUNT DISTRIBUTION ===")
    for count in sorted(clue_distribution.keys()):
        print(f"{count:2d} clues: {clue_distribution[count]:3d} puzzles")
    print()
    
    # Answer analysis
    print("=== ANSWER ANALYSIS ===")
    print(f"Unique answers: {len(answers)}")
    print(f"Duplicate answers found: {len(duplicate_answers)}")
    
    if duplicate_answers:
        print("\nDuplicate answers:")
        for answer in sorted(duplicate_answers):
            print(f"  {answer}")
    print()
    
    # # Sample puzzles with extreme clue counts
    # print("=== SAMPLE PUZZLES ===")
    # min_clue_puzzles = [(i+1, puzzle_str, clue_counts[i]) 
    #                     for i, (puzzle_str, _, _) in enumerate(puzzles) 
    #                     if clue_counts[i] == min_clues][:3]
    
    # max_clue_puzzles = [(i+1, puzzle_str, clue_counts[i]) 
    #                     for i, (puzzle_str, _, _) in enumerate(puzzles) 
    #                     if clue_counts[i] == max_clues][:3]
    
    # print(f"Sample puzzles with minimum clues ({min_clues}):")
    # for puzzle_num, puzzle_str, clue_count in min_clue_puzzles:
    #     print(f"  Puzzle {puzzle_num}: {puzzle_str} ({clue_count} clues)")
    
    # print(f"\nSample puzzles with maximum clues ({max_clues}):")
    # for puzzle_num, puzzle_str, clue_count in max_clue_puzzles:
    #     print(f"  Puzzle {puzzle_num}: {puzzle_str} ({clue_count} clues)")

def main():
    parser = argparse.ArgumentParser(description='Analyze puzzle statistics from a testsuite file.')
    parser.add_argument('filename', type=str, help='Path to the testsuite file')
    
    args = parser.parse_args()
    
    analyze_puzzles(args.filename)

if __name__ == '__main__':
    main() 