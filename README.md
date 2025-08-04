# Lime Sudoku 
## (aka Minesweeper Sudoku / Sudoku Mine / Blueberry Trio)

This will be a constructor for Minesweeper Sudoku, written in Python.

First video in series: https://www.youtube.com/watch?v=LftLt_dmlu8

## Steps to constructing a puzzle

1. Pick a puzzle
2. Get some samples, if you can
3. Make a brute force solver
4. Make a generator
5. Make a bunch of puzzles
6. Write a new, better solver

### More about these steps.

Step 2: We make a small test suite by collecting a few puzzles from the Internet and transcribing them for our solver. The purpose of the small test suite is to help us bootstrap writing a solver/generator.  Once we've written a working generator, we can throw out those puzzles and generate a much larger test suite with thousands of puzzles.

Step 3: The purpose of the brute force solver is to
* make it easier to write the initial generator (the hardest part of the generator is the solver)
* allow us to generate a wide variety of puzzles, including easy, hard, and intractible puzzles.

Step 6: The purpose of the better solver in step 6 is to do a better job at detecting and distinguishing between puzzles that are easy, hard, and intractible.  We don't want to publish intractible puzzles, and we want to be able to group our puzzles into difficulty tiers.

