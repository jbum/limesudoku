from layout_classic import Layout
from layout_jiggy9 import Layout as JiggyLayout
import json
import random

class PuzzleRecord():
    def __init__(self, clues_string, layout, puzzle_type, nom='untitled-puzzle', answer_string=None):
        self.clues_string = clues_string
        self.layout = layout
        self.puzzle_type = puzzle_type
        self.annotations = {}
        self.answer_string = answer_string
        self.nom = nom
        self.solution = None

    def add_annotation(self, key, value):
        self.annotations[key] = value

    def change_clue(self, idx, value):
        self.clues_string = self.clues_string[:idx] + value + self.clues_string[idx+1:]

    def clone(self):
        return PuzzleRecord(self.clues_string, self.layout, self.puzzle_type, self.nom, self.answer_string)

    def __str__(self):
        annotation_string = ','.join([f"{k}:{v}" for k,v in self.annotations.items()])
        return f"{self.nom}\t{self.layout.get_prefix()}\t{self.clues_string}\t{self.answer_string if self.answer_string else ''}\t{json.dumps(self.annotations)}"

    @classmethod
    def parse_puzzle(cls, line):
        """
        Parse a line from a puzzle file and return a PuzzleRecord instance.
        Expects a tab-separated line with fields:
        nom, puzzle_type, [layout], clues_string, [answer_string], [annotations]
        """
        parts = line.split('\t')
        nom = parts[0]
        parts = parts[1:]
        ptype = parts[0]
        parts = parts[1:]
        if 'jiggy' in ptype:
            layout = parts[0]
            parts = parts[1:]
        else:
            layout = None
        puzzle_str = parts[0]
        if len(puzzle_str) != 81:
            raise ValueError(f"Invalid puzzle length {len(puzzle_str)} for puzzle: {puzzle_str!r}")
        valid_chars = set('.012345678')
        if not all(c in valid_chars for c in puzzle_str):
            raise ValueError(f"Invalid characters in puzzle: {puzzle_str!r}")

        parts = parts[1:]
        answer_str = None
        if len(parts[0]) == 81:
            answer_str = parts[0]
            parts = parts[1:]
        elif len(parts[0]) == 0:
            answer_str = None
            parts = parts[1:]
        else:
            answer_str = None
        comment = '' # 'ans='+answer_str

        if 'jiggy' in 'ptype':
            layout = JiggyLayout(9, ptype, layout_string)
        else:
            layout = Layout(9, ptype)

        return cls(puzzle_str, layout, ptype, nom, answer_str)

    @classmethod
    def setup_initial_clues(cls, sol, layout):
        num_symbols = layout.num_symbols
        clues = []
        # loop on x,y in the grid
        for y in range(num_symbols):
            for x in range(num_symbols):
                addr = x + y * num_symbols
                if sol[addr] == '.':
                    # count the neighboring circles
                    count = 0
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            nx = x + dx
                            ny = y + dy
                            if nx >= 0 and nx < num_symbols and ny >= 0 and ny < num_symbols:
                                naddr = nx + ny * num_symbols
                                if sol[naddr] == 'O':
                                    count += 1
                    clues.append((addr, count))
                else:
                    clues.append((addr, None))

        # convert clues to a string of numbers or '.'
        clue_str = ''
        for clue in clues:
            if clue[1] is None:
                clue_str += '.'
            else:
                clue_str += str(clue[1])
        # !! for each cell, if empty, count the neighboring circles, otherwise, omit the clue
        # save this into self.clues - should be kept separtely from the solution?
        # then return as separate element of the return tuple

        return clue_str

    @classmethod
    def generate_candidate_answer(cls, layout, ptype, nom):
        # ....
        # localized for limesweeper - this is correct apparently
        """Generate a valid Lime puzzle solution with exactly 3 circles per row/column/container."""

        area = layout.area
        num_symbols = layout.num_symbols

        # Start with empty grid
        solution = '.' * area

        solution = '..O....OOO..O.O....O..O.O..OO....O....OOO.........O.OO...O.O..OOO....O....O.O..O.'
        
        # Helper function to check if adding a circle at addr would be valid
        def can_add_circle(addr, current_sol):
            row = addr // num_symbols
            col = addr % num_symbols
                
            # Check containers
            for container in layout.containers:
                if addr in container:
                    if sum(1 for cell in container if current_sol[cell] == 'O') >= 3:
                        return False
                        
            return True
        
        # Try to place circles
        attempts = 0
        while True:
            attempts += 1
            if attempts > 1000:  # Prevent infinite loops
                return None, None
                
            current_sol = solution
            placed_circles = sum(1 for c in current_sol if c == 'O')

            # ? place any circles that are forced by the layout

            # Try to place 27 circles (3 per row)
            while placed_circles < 27:
                # Get all valid positions
                valid_positions = [i for i in range(area) if current_sol[i] == '.' and can_add_circle(i, current_sol)]
                if not valid_positions:
                    break
                    
                # Choose a random valid position
                pos = random.choice(valid_positions)
                current_sol = current_sol[:pos] + 'O' + current_sol[pos+1:]
                placed_circles += 1
                
            # Check if we have a valid solution
            if placed_circles == 27:
                # Verify all constraints
                valid = True
                for container in layout.containers:
                    if sum(1 for cell in container if current_sol[cell] == 'O') != 3:
                        valid = False
                        break
                            
                if valid:
                    initial_puz_str = cls.setup_initial_clues(current_sol, layout)
                    return current_sol, initial_puz_str
                    
            # If we didn't get a valid solution, try again
            solution = '.' * area

    @classmethod
    def generate_candidate_puzzle(cls, layout, ptype, nom, allow_zeros=False):
        answer_string, initial_puz_str = cls.generate_candidate_answer(layout, ptype, nom)
        # print("ANSWER STRING", answer_string)
        # print("INITIAL PUZ STRING", initial_puz_str)
        if len(answer_string) != 81:
                raise ValueError("Answer string must be 81 characters long")
            
        # # Convert answer string to 2D grid for easier processing
        # grid = []
        # for i in range(9):
        #     row = []
        #     for j in range(9):
        #         idx = i * 9 + j
        #         row.append(1 if answer_string[idx] == 'O' else 0)
        #     grid.append(row)
        
        # # Generate clued puzzle
        # clued_puzzle = []
        # for i in range(9):
        #     for j in range(9):
        #         if grid[i][j] == 1:  # Mine
        #             clued_puzzle.append('.')
        #         else:  # Count adjacent mines
        #             count = 0
        #             for di in [-1, 0, 1]:
        #                 for dj in [-1, 0, 1]:
        #                     if di == 0 and dj == 0:
        #                         continue
        #                     ni, nj = i + di, j + dj
        #                     if 0 <= ni < 9 and 0 <= nj < 9:
        #                         count += grid[ni][nj]
        #             clued_puzzle.append(str(count))

        # puzzle_str = ''.join(clued_puzzle)
        if not allow_zeros:
            # remove the zeros
            initial_puz_str = initial_puz_str.replace('0', '.')
        # attempt to solve it, if we can't solve it return None
        prec = cls(initial_puz_str, layout, ptype, nom=nom, answer_string=answer_string)
        return prec