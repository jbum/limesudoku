Lime Sudoku (aka Minesweeper Sudoku / Sudoku Mine / Blueberry Trio)

This will be a constructor for Minesweeper Sudoku, written in Python.

First video in series: https://www.youtube.com/watch?v=LftLt_dmlu8

### Steps to constructing a puzzle

1. Pick a puzzle
2. Get some samples, if you can
3. Make a brute force solver
4. Make a generator
5. Make a bunch of puzzles
6. Write a new, better solver

More about these steps.

The purpose of the small test suite collected in step 2 is to help us bootstrap writing a solver/generator.  Once we've written a working generator, we can throw out those puzzles and generate a much larger test suite.

The purpose of the brute force solver in step 3 is to
* make it easier to write the generator (the hardest part of the generator is the solver)
* allow us to generate a wide variety of puzzles, including easy, hard, and intractible puzzles.

; so we can then write a better solver which is capable of detecting puzzle difficulty, and capable of distinguishing between "fun" puzzles and tedious / intractible puzzles.

The purpose of the better solver in step 6 is to do a better job at detecting and distinguishing between puzzles that are easy, hard, and intractible.  We don't want to publish intractible puzzles, and we want to be able to group our puzzles into difficulty tiers.

