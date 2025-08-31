# Rules Bestiary

## Easy Rules

### Rules of Container Cleanup

*If a container has 3 mines, the remaining cells must be empty.*

In the following example, we are cleaning up the 3x3 block on the upper left, as well as row 2, and row 8.

| Before | After |
|--------|-------|
| ![E1 before](/rule_drawings/rule_EContCa_before.png "Easy Container Cleanup BEFORE") | ![E1 after](/rule_drawings/rule_EContCa_after.png "Easy Container Cleanup AFTER") |

---

*If a container has 6 empties (including clued cells), the remaining cells must be mines.*

In the following example, we are placing the remaaining mines in the middle 3x3 block, as well as column 6.
| Before | After |
|--------|-------|
| ![E1 before](/rule_drawings/rule_EContCb_before.png "Easy Container Cleanup BEFORE") | ![E1 after](/rule_drawings/rule_EContCb_after.png "Easy Container Cleanup AFTER") |

---

### Rules of Clue Cleanup

*If a clue has all its mines, its remaining neighbors can be cleared.*

In the following example, we are cleaning up the first 1-clue in row 1, the 3-clue in row 4, the 1-clue in row 6, and the 3-clue in row 7. 

| Before | After |
|--------|-------|
| ![E1 before](/rule_drawings/rule_EClueCa_before.png "Easy Clue Cleanup BEFORE") | ![E1 after](/rule_drawings/rule_EClueCa_after.png "Easy Clue Cleanup AFTER") |

---

*If a clue has all its empties (#neighbors-#empties==clue), the remaining neighbors must be mines.*

In the following example, we are placing remaining mines for the 5-clue in row 2, the 4-clue in row 6, and the 2-clue in row 9.


| Before | After |
|--------|-------|
| ![E1 before](/rule_drawings/rule_EClueCb_before.png "Easy Clue Cleanup BEFORE") | ![E1 after](/rule_drawings/rule_EClueCb_after.png "Easy Clue Cleanup AFTER") |

---

## Medium Rules

### Greedy Clues

*If a clue must use at least 3 mines within the same container, the remaining cells in that container must be empty.*

In the following example, the 3-clue in the upper 3x3 block requires 3 mines, so the 3 cells in that block that aren't neighboring the 3 must be empty.

| Before | After |
|--------|-------|
| ![E1 before](/rule_drawings/rule_MGreedyClues_before.png "Greedy Clues BEFORE") | ![E1 after](/rule_drawings/rule_MGreedyClues_after.png "Greedy Clues AFTER") |


*If a clue straddles two containers such that 3 mines are forced in one, and its remaining mines are forced in another, than we can clear cells from one container, and force mines in the other.*


In the following example, the 4-clue on the right side of row 8 has only 1 external cell outside of the lower-right 3x3 block. It must use 3 cells in that corner block (enabling us to clear the block's remaining cells), and the external cell is forced to be a mine.

| Before | After |
|--------|-------|
| ![E1 before](/rule_drawings/rule_MGreedyCluesGeneral_before.png "Greedy Clues BEFORE") | ![E1 after](/rule_drawings/rule_MGreedyCluesGeneral_after.png "Greedy Clues AFTER") |


---

### Pushy Clues

*In a container, if a clue is n, and the number of external (not neighboring) mines + external blanks == 3-n, the external blanks must be mines.*

*Corollary: when this happens, it implies that the in-container neighboring cells must contain all the clue's mines, so we can clear the unknown-neighbors of the clue that are not in the container-of-interest*

In the following example, the 1-clue in row 4 must use 1 of its two neighboring cells in its containing 3x3 block. This forces a mine in the non-neighboring cell in that block, and forces its external neighbors to be empty.


| Before | After |
|--------|-------|
| ![E1 before](/rule_drawings/rule_MPushyOnes_before.png "Pushy Ones BEFORE") | ![E1 after](/rule_drawings/rule_MPushyOnes_after.png "Pushy Ones AFTER") |

----

### At-Least-1 Containers

*If a container contains an at-least-1 group that would finish the container, then the remaining unknown in the container (not in that group) can be cleared.*

This is very similar to "pushy-clues", but can catch container->container interactions.

In the example below, the 3x3 block on the upper left already has two mines, so it's remaining two cells in row 1 form an at-least-1 pair. This forces the remaining mine for row 1, so we can clear its uninvolved cells.

| Before | After |
|--------|-------|
| ![E1 before](/rule_drawings/rule_MalCont_before.png "Pushy Ones BEFORE") | ![E1 after](/rule_drawings/rule_MalCont_after.png "Pushy Ones AFTER") |

----

### At-Least-1 Clues

*If a clue's neighbors contain an entire at-least-1 group that would finish the clue, then the remaining unknown neighbors (not in that group) can be cleared.*

In the following example, the second 2-clue in row 7 has a forced mine below it (due to container crowding).  This forces the neighboring cells above it to be cleared.

| Before | After |
|--------|-------|
| ![E1 before](/rule_drawings/rule_MalClue_before.png "Pushy Ones BEFORE") | ![E1 after](/rule_drawings/rule_MalClue_after.png "Pushy Ones AFTER") |


---

### At-Most-1 Containers

*If a container contains an at-most-1 group, and 2 other cells remain, then those 2 cells must be mines. More generally, if the number of remaining unknown cells in the container is equal to (3 - the number of known mines in the container - 1), then those remaining cells must be mines.*

In the following example, row 3 contains 2 cells on the right that can hold no more than 1 cell, so the two unknown cells on the left side must be mines.

| Before | After |
|--------|-------|
| ![E1 before](/rule_drawings/rule_MamCont_before.png "Pushy Ones BEFORE") | ![E1 after](/rule_drawings/rule_MamCont_after.png "Pushy Ones AFTER") |


### At-Most-1 Clues

*If a clue contains an at-most-1 group (due to interactions with containers or other clues), and the #remaining-open-cells in that clue are equal to (clue# - clue.known.mines - 1), then we can set the remaining open cells in the clue to mines*

In the following example, the cells neighboring both the 1-clue and the 4-clue in row 3 can hold at-most 1 mine (due to the presence of the 1). This forces mines into the 3 remaining unknown cells of the 4-clue. 

| Before | After |
|--------|-------|
| ![E1 before](/rule_drawings/rule_MamClue_before.png "Pushy Ones BEFORE") | ![E1 after](/rule_drawings/rule_MamClue_after.png "Pushy Ones AFTER") |



----

## Hard Rules

### Rule of Subgroups

This is a very general set of rules that covers ALL the situations described by the medium rules, and several more (due to 2nd and 3rd order effects), enabling us to solve far more puzzles without trial and error.  However, the situations caught by this rule are typically more subtle than the medium rules, involving chain-reactions, so this strategy contributes significantly more to the difficulty score of the puzzle.  

The basic algorithm is this:

1. Identify all the at-least-N and at-most-N groups using the containers, and the clues.
2. Use the interactions between those groups to identify more sub-groups.
    1. *If a clue's unknowns are a subset of an at-least-group N with length P and order M then the intersecting cells >= order can be computed as at-least M-(P-len(intersection)) because all subgroups of length M of an at-least subgroup ord N with length P are at-least (P-M)*
    2. *An at-least-N that is a full subset of an at-most-N+ (V) forces the remainder cells to at-most-(V-N)*
    3. *An at-most that is (fully or partially) inside an at-least of greater order, makes the remainder at-least (outer.ord-inner.ord)*
3. Keep re-executing step 2 until no more subgroups are found or some desired maximum iterations is hit.
4. Use the resultant subgroups to find clears and mines:
    1. *An at-least-N that is a full subset of an at-most-N (same n), empties the intersection of the two sets.*
    2. *An at-least-N group that has a length of N can be set to mines.*
    3. *An at-most-N group that has an ord of 0 can be cleared*

In the following example, the 2-clue in column 5 shares neighbors with the 4-clue above it, and those shared neighbors form an at-most 2 group.  This forces the remaining neighbors of the 4-clue to be at-least-2, and since there are only two of them, they must be mines.

In addition, D8 and E8 can be cleared, since the shared neighbors of the 4-clue and 2-clue in column 5 form an at-least-2 group.  The two cleared cells are the intersection of the at-most-2 group of the 2-clue's neighbors and the at-least-2 group of the 4-clue's shared neighbors.

| Before | After |
|--------|-------|
| ![E1 before](/rule_drawings/rule_Hsubgroups_a_before.png "Pushy Ones BEFORE") | ![E1 after](/rule_drawings/rule_Hsubgroups_a_after.png "Pushy Ones AFTER") |

Continuing with the same puzzle, we have a subtle chain-reaction.

H6, and H7 form an at-least-1 group, since at least one must be used for the 3-clue in column 9. Since one of those must be used, the remaining neighbors of the 3 in column 7 form an at-most-2 group. This forces the 3 bottom neighbors of the 4-clue in in column 6 to be an at-least-2, sucking up a lot of room from the bottom row.  The remaining empty cells in that row are at-most-1.  Since two of those at-most-1 cells neighbor the 3-clue in column 3, they force its remaining cells to be mines. 

| Before | After |
|--------|-------|
| ![E1 before](/rule_drawings/rule_Hsubgroups_b_before.png "Pushy Ones BEFORE") | ![E1 after](/rule_drawings/rule_Hsubgroups_b_after.png "Pushy Ones AFTER") |


In the example below, The 3-clue in column 3, must use at-least 1 cell from its neighbors in row 9.  This forces the remaining cells in row 9 to be at-most-2, which forces the remaining neighbors of the 4-clue in column 6 to be mines.

Since cells H6,H7 form an at-least-1 (due to the 3 in column 9), we can eliminate the uninvolved neighbors cells of the 3 in column 7 (F6, G6, H8).  

The 3 mines in row 9 must go adjacent to the 3 in column 3, and the 4 in column 6. This allows us to clear the remaining empty cells in row 9.

| Before | After |
|--------|-------|
| ![E1 before](/rule_drawings/rule_Hsubgroups_c_before.png "Pushy Ones BEFORE") | ![E1 after](/rule_drawings/rule_Hsubgroups_c_after.png "Pushy Ones AFTER") |
