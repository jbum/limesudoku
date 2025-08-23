# Lime Sudoku 
## (aka Minesweeper Sudoku / Sudoku Mine / Blueberry Trio)

This will be a constructor for Minesweeper Sudoku, written in Python.

First video in series: https://www.youtube.com/watch?v=LftLt_dmlu8

## HISTORY

### 8/5/2025

Prompts:
1. Make a new script for generating puzzles.  gen_puzzles.py. It'll use argparse to get some optional params -n <nbr_puzzles> and -r <random_seed>. Number puzzles defaults to 1, random seed defaults to 0.  It'll loop and produce each puzzle, one per line, using the format In my testsuites/sample_puzzles.tsv file.  The generate_puzzles function should call generate_candidate_answer, generate_fully_clued_puzzle, and refine_puzzle.  generate_candidate_answer, should use the method in test_random.py to generate a random answer string.  generate_fully_clued_puzzle will generate a string where each mine is a dot, and every other square is the number of adjacent mines.  Leave refine_puzzle blank for now and just have it return the fully-clued puzzle that is passed into it.  
2. Okay, the refine_puzzle will do three refinement_passes.  In each one, it will start with the fully-clued puzzle and remove clues, randomly (using a shuffled address list), one-at-a-time.  It will then call solve() on the modified puzzle, with no other arguments.  If the solver does not return an 81 character string, then it will restore the deleted clue, since it's necessary to solve the puzzle.  After going through all the clues, the remaining clues are necessary.  It will keep the puzzle with the fewest number of clues after the 3 passes, and return that.
3. In the main function please add some elapsed time measurement and report it at the end.
(Manually fixed issue with seeding random generator)

### 8/6/2025

- Added command line feedback comment using CMD-K
- Manually fixed it to make zero-clues optional, default is no zeros

### 8/7/2025

- Added support for annotations in solver.  Reporting on OR-Tools branch count.  Regenerated test suites with this info.

### 8/19/2025

- Added support for multiple solvers via --solver param.
- Added preliminiary PR (production-rule) solver.

### 8/20/2025

- Added --max-tier parameter to limit difficulty of output puzzles when used with PR solver.
- Modified solvers to put most optional arguments in a dictionary.

### 8/22/2025

- Added --min-tier parameter to limit difficulty of output puzzles when used with PR solver.
- Added --reduction_passes parameter to control number of refinement passes.

