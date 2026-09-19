# Step-by-step solutions (lime_steps.py)

How the Lime Sudoku puzzles on krazydad.com get their "Show next step" solutions. The website
side (the JSON endpoint, the overlay) is documented in `krazydad/limesudoku/steps/README.md`;
the Star Battle equivalent, which this follows, in `starbattle/STEPS.md`.

## Pipeline

```
/limesudoku/steps/api.php  (website, on mertz)
   | resolves the puzzle id through the /play API to type, clues and (jigsaw) layout
   | caches the result in esc by puzzle id
   v
cd /home/jbum/Development/puzzles/limesudoku            (this repo, cloned on mertz)
pypy3 lime_steps.py --type lime-jigsaw --layout AAAB... --clues ..2..1.. --id KD_lime-jigsaw_V1-B1-P1
   |  solve_PR.solve(rec, {'log_steps': True})   the production-rule solver with its step log on
   |  lime_steps.build_steps()                   groups the log into steps, writes captions
   v
JSON on stdout
```

`pypy3 lime_steps.py --file puzzledata/lime-hard-V1.tsv --index 7 --text` prints a puzzle's
captions for review.

## The step log (solve_PR.py)

With `log_steps` on, `clear_cell()` and `set_cell_mine()` append to `board.log`:
`{'cmd': 'CLEAR'|'MINE', 'addr': (x,y), 'rule': shortnom, 'pass': n, 'prov': {...}}`. Every rule
now collects its deductions in a dict (cell -> provenance) instead of a set and applies them
through `apply_found()`, so the provenance is recorded at the moment the rule finds the cell;
the first reason found for a cell is the one kept. Nothing else changed: the grading output
(`work`, `mta`, `logic_history`) of every puzzle file in `puzzledata/` is byte-identical to
before the instrumentation (checked 2026-09-19 with `solve_puzzles.py -pp`).

Provenance kinds, by rule:

| rule (shortnom) | `prov.kind` | what it carries |
|---|---|---|
| ECx container cleanup | `cont-full`, `cont-empties` | container index, its mines / empties |
| Ecx clue cleanup | `clue-full`, `clue-empties` | clue cell, value, its mines / unknowns |
| Mgc greedy clues | `greedy` | clue, container, the clue's open neighbors |
| Mgcg greedy general | `greedy-general` | clue, forcing container, rest container, neighbors in each |
| Mpc pushy clues | `pushy` | clue, container, external squares, neighbors in/out of the container |
| MamC / Mamc at-most-1 | `atmost1-cont`, `atmost1-clue` | subject, the at-most-1 group and its source (`src`: a container with two limes or a clue needing one) |
| MalC / Malc at-least-1 | `atleast1-cont`, `atleast1-clue`, `atleast1-clue-cont` | subject, the at-least-1 group and its source |
| Hsg1 / Hjigsg1 / Hjigsg2 subgroups | `sg-mines`, `sg-clear-zero`, `sg-clear-subset`, `sg-clear-diff` | group indexes into `groups`, the rule call's whole group list |
| HjigLg jigsaw bump logic | `jig-bump` | axis, split line, hole and bump squares, the lime count, which side was deduced |

Subgroups carry a structured `src` as well as the old `source` string: base groups
`{'kind':'cont'|'clue'|'jig-lines', ...}`, derived groups `{'kind':'intersect'|
'atmost-minus-atleast'|'atleast-minus-atmost', parent/outer/inner indexes}`.

`draw_limesudoku` (pycairo) is now imported lazily, so the solver runs on a host without cairo.

## Steps and captions (lime_steps.py)

A step is one rule firing for one subject (`step_key()`: the container, the clue, the group).
Cells are named `A1`..`I9` (column letter, row number). Output:

```
{"puzzleID": ..., "puzz_data": {"version", "gw": 9, "gh": 9, "type", "clues", "layout", "answer" ("" if unsolved), "work", "tier"},
 "steps": [{"step", "rule", "kind",
            "mines": "A1,..", "empties": "..",      cumulative state after the step
            "hi4s": "..",                           this step's new marks (yellow)
            "his": green squares, "hi6s": orange squares, "hi8s": gray squares,
            "hic": clues to circle (in caption order: blue, red, green, orange),
            "rhi": {"rows": [3], "cols": [7], "outlines": ["A1,B1,..", ...]},
            "caption": "..."}, ..., {"step": N, "mines", "empties", "caption": "Ta-da!"}]}
```

Captions never name coordinates (the pages show none): they say "the circled 3", "row 4",
"the top-left block", "the outlined shape" (or "the pink-outlined shape" when several are
outlined), "the upper-left window", and refer to squares by color. `Naming` resolves the
container and clue names once a caption is complete, so the colors follow the order of mention.

The subgroup rule is the hard one to narrate. `explain_group()` writes the sentences that
establish a group's bound one derivation deep, using a second color (orange, or gray when the
caption already uses orange) for the auxiliary squares; a deeper derivation is stated plainly
as following "from combining the surrounding clues and regions" rather than nested in
parentheses.

## Checks

Over every live file (`puzzledata/lime-*-V?.tsv`, `puzzledata/daily/lime-daily-*.tsv`): all
puzzles solve, the final step's limes equal the answer, and no caption falls back to a
placeholder. `lime_steps.py --text` on a handful of hard and jigsaw puzzles is the review tool.

Deploying: commit, push, `ssh mertz "cd /home/jbum/Development/puzzles/limesudoku && git pull"`.
The website caches by puzzle id (`&ignatz` refetches one).
