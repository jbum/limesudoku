#!/usr/bin/env python3
#
# measure_puzzles.py - Analyze puzzle statistics from a testsuite file
# Based on the file loading method from solve_puzzles.py

import sys
from solve_puzzles import read_puzzles_from_file

def count_clues(puzzle_str):
    """Count the number of clues (non-dot characters) in a puzzle string."""
    return sum(1 for c in puzzle_str if c != '.')

def analyze_puzzles(filename):
    """Analyze puzzles from a testsuite file and print statistics."""
    puzzles = read_puzzles_from_file(filename)
    
    if not puzzles:
        print("No valid puzzles found in the file.")
        return
    
    # print(f"Found {len(puzzles)} valid puzzles.\n")
    
    # Calculate clue counts and collect answers
    clue_counts = []
    answers = set()
    duplicate_answers = set()
    
    for i, puzrec in enumerate(puzzles, 1):
        puzzle_str = puzrec['puzzle']
        answer_str = puzrec['answer']
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
    
    # Clue count distribution
    clue_distribution = {}
    for count in clue_counts:
        clue_distribution[count] = clue_distribution.get(count, 0) + 1


    # Print statistics
    print(f"Tot puzzles: {len(puzzles)} | Tot clues: {total_clues} | Avg clues: {avg_clue_count:.2f} | Min clues: {min_clues} | Max clues: {max_clues} | Dupes: {len(duplicate_answers)}")
    print("Clue Distribution: ", ', '.join(f"{count}:{clue_distribution[count]}" for count in sorted(clue_distribution.keys())))
    
    
    
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
    import argparse

    parser = argparse.ArgumentParser(description='Analyze puzzle statistics from a testsuite file.')
    parser.add_argument('filename', nargs='+', type=str, help='Path to the testsuite file')
    
    args = parser.parse_args()
    for filename in args.filename:
        if len(args.filename) > 1:
            print(f"{filename}:")
        analyze_puzzles(filename)
        print()

if __name__ == '__main__':
    main() 