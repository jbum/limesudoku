# solve_PR.py
#
# PRODUCTION RULE solver for Minesweeper Sudoku

CELL_UNKNOWN = 0
CELL_EMPTY = 1
CELL_MINE = 2

class Cell:
    def __init__(self, x, y, value_str):
        self.x = x
        self.y = y
        self.clue = None
        self.value = CELL_UNKNOWN
        self.known_value = None
        if value_str in '0123456789':
            self.clue = int(value_str)
            self.value = CELL_EMPTY
        elif value_str == 'O':
            self.clue = None
            self.value = CELL_MINE

class PuzzleBoard:
    def __init__(self, puzzle_str, known_answer_str=None, layout='AAABBBCCCAAABBBCCCAAABBBCCCDDDEEEFFFDDDEEEFFFDDDEEEFFFGGGHHHIIIGGGHHHIIIGGGHHHIII'):
        self.puzzle_str = puzzle_str
        self.known_answer_str = puzzle_str
        self.layout = layout
        self.board = {}
        self.gw = 9
        self.gh = 9
        self.area = self.gw * self.gh
        for i in range(self.area):
            x,y = i % self.gw, i // self.gw
            self.board[x,y] = Cell(x,y, puzzle_str[i])
            if known_answer_str:
                self.board[x,y].known_value = CELL_MINE if known_answer_str[i] == 'O' else CELL_EMPTY

        # setup containers
        self.containers = []
        # set up rows
        for y in range(self.gh):
            cont = []
            for x in range(self.gw):
                cont.append((x,y))
            self.containers.append(cont)
        # set up columns
        for x in range(self.gw):
            cont = []
            for y in range(self.gh):
                cont.append((x,y))
            self.containers.append(cont)
        # set up layout - this supports jigsaw puzzles as well as traditional puzzles
        for i in range(len(self.layout)):
            for letter in 'ABCDEFGHI':
                cont = []
                if self.layout[i] == letter:
                    cont.append((x,y))
            self.containers.append(cont)

    def clear_cell(self, x, y, why='generic_reason'):
        if self.board[x,y].known_value is not None:
            if self.board[x,y].known_value != CELL_EMPTY:
                raise Exception(f'mismatched clear: x={x} y={y} {self.board[x,y].known_value=} rule {why=}')
        self.board[x,y].value = CELL_EMPTY

    def set_cell_mine(self, x, y, why='generic_reason'):
        if self.board[x,y].known_value is not None:
            if self.board[x,y].known_value != CELL_MINE:
                raise Exception(f'mismatched set: x={x} y={y} {self.board[x,y].known_value}= rule {why=}')
        self.board[x,y].value = CELL_MINE


    def tally_container_cells(self, cont):
        tallies = [[],[],[]]
        for x,y in cont:
            cell = self.board[x,y]
            tallies[cell.value].append((x,y))
        return tallies

    def rule_easy_container_completion(self):
        made_progress = False
        clears = []
        sets = []
        for cont in self.containers:
            tallies = self.tally_container_cells(cont)
            if len(tallies[CELL_UNKNOWN]) == 0: # container is already solved?
                continue
            if len(tallies[CELL_MINE]) == 3: # container is already solved?
                for x,y in tallies[CELL_UNKNOWN]:
                    clears.append((x,y))
            if len(tallies[CELL_EMPTY]) == 6: # container is already solved?
                for x,y in tallies[CELL_UNKNOWN]:
                    sets.append((x,y))
        # having gone through all containers, we can apply the sets and clears
        for x,y in clears:
            self.clear_cell(x,y)
            made_progress = True
        for x,y in sets:
            self.set_cell_mine(x,y)
            made_progress = True
        return made_progress

    def solution_found(self):
        for cell in self.board.values():
            if cell.value == CELL_UNKNOWN:
                return False
        return True
    
    def solution_string_found(self):
        solution_str = ''
        for cell in self.board.values():
            solution_str += 'O' if cell.value == CELL_MINE else '.'
        return solution_str
    
    
    def rule_easy_greedy_clues(self):
        # todo...
        return False
            
    def __str__(self):
        return self.puzzle_str

production_rules = [{'score':1, 'nom':'container-completion', 'function':PuzzleBoard.rule_easy_container_completion},
                    {'score':2, 'nom':'greedy-clues', 'function':PuzzleBoard.rule_easy_greedy_clues},
                    ]

def solve(puzzle_str, known_answer_str=None, rand_seed = 1, max_solutions = 2, layout='AAABBBCCCAAABBBCCCAAABBBCCCDDDEEEFFFDDDEEEFFFDDDEEEFFFGGGHHHIIIGGGHHHIIIGGGHHHIII'):
    board = PuzzleBoard(puzzle_str, known_answer_str, layout=layout)
    try:
        solution_found = False
        work = 0
        while True:
            if board.solution_found():
                solution_found = True
                break
            made_progress = False
            for rule in production_rules:
                if rule['function'](board):
                    made_progress = True
                    work += rule['score']
                    break
            if not made_progress:
                break
        if solution_found:
            sol_string_found = board.solution_string_found()
            if known_answer_str is not None and sol_string_found != known_answer_str:
                raise Exception(f'solution found but does not match known answer: {sol_string_found=} {known_answer_str=}')
            else:
                return sol_string_found, {'work':work}
        else:
            return "no solution",{'work':work}
    except Exception as e:
        print(f'error: {e}')
        return False,{}

    assert False # should never get here


if __name__ == '__main__':
    puzzle_str = '..32.......3...........1......3....4......4.2......43..3..................33..1..' # easy
    puzzle_str = '1..11..32.............3..332.33.23.32...3....2..3.33323.333..21.......3.1...22.21' # ridiculously easy
    solution,stats = solve(puzzle_str)
    print(f'{solution=} {stats=}')
