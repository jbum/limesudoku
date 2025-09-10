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
        prec = PuzzleRecord(self.clues_string, self.layout, self.puzzle_type, self.nom, self.answer_string)
        prec.solution = self.solution
        prec.annotations = self.annotations.copy()
        return prec
        # return PuzzleRecord(self.clues_string, self.layout, self.puzzle_type, self.nom, self.answer_string)

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
                    clues.append(str(count))
                else:
                    clues.append('.')

        # convert clues to a string of numbers or '.'
        return ''.join(clues)

    @classmethod
    def generate_candidate_answer(cls, layout, ptype, nom):
        # ....
        # localized for limesweeper - this is correct apparently
        """Generate a valid Lime puzzle solution with exactly 3 circles per row/column/container."""

        area = layout.area
        num_symbols = layout.num_symbols

        # Start with empty grid
        solution = list('.' * area)
        

        # Try to place circles
        attempts = 0
        while True:
            attempts += 1
            if attempts > 1000:  # Prevent infinite loops
                return None
                
            current_sol = list(solution) # clone it
            placed_circles = 0

            # Try to place 27 circles (3 per row)
            valid_positions = set([i for i in range(area)])
            while placed_circles < 27:
                for cont in layout.containers:
                    if sum(1 for cell in cont if current_sol[cell] == 'O') == 3:
                        valid_positions -= set(cont)
                if len(valid_positions) == 0:
                    break
                
                # convert to list
                pos = random.choice(list(valid_positions))
                current_sol[pos] = 'O'
                valid_positions.discard(pos)
                placed_circles += 1
                
            # will only execute if we didn't break (which means we have 27 circles)
            else:
                return current_sol

            # If we didn't get a valid solution, the loop continues to execute

    @classmethod
    def generate_candidate_puzzle(cls, layout, ptype, nom, allow_zeros=False):
        answer = cls.generate_candidate_answer(layout, ptype, nom)
        if answer == None or len(answer) != 81:
                raise ValueError("Answer string must be 81 characters long")
        initial_puz_str = cls.setup_initial_clues(answer, layout)
        if not allow_zeros:
            # remove the zeros
            initial_puz_str = initial_puz_str.replace('0', '.')
        print("candidate puzzle", initial_puz_str, answer, layout.containers)
        prec = cls(initial_puz_str, layout, ptype, nom=nom, answer_string=''.join(answer))
        return prec