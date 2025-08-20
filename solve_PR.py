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
        for letter in 'ABCDEFGHI':
            cont = []
            for i in range(len(self.layout)):
                x,y = i % self.gw, i // self.gh
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


    def split_cells_by_value(self, cont):
        tallies = [[],[],[]]
        for x,y in cont:
            cell = self.board[x,y]
            tallies[cell.value].append((x,y))
        return tallies

    def get_neighbor_coords(self, x, y):
        neighbor_coords = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < 9 and 0 <= ny < 9:
                    neighbor_coords.append((nx, ny))
        return neighbor_coords

    def solution_found(self):
        for cell in self.board.values():
            if cell.value == CELL_UNKNOWN:
                return False
        return True
    
    def solution_string_found(self):
        solution_str = ''
        for cell in self.board.values():
            solution_str += 'O' if cell.value == CELL_MINE else '?' if cell.value == CELL_UNKNOWN else '.'
        return solution_str


    def rule_easy_container_completion(self):
        made_progress = False
        clears = set()
        sets = set()
        for cont in self.containers:
            splits = self.split_cells_by_value(cont)
            if len(splits[CELL_UNKNOWN]) == 0: # container is already solved?
                continue
            if len(splits[CELL_MINE]) == 3: # container is already solved?
                clears.update(splits[CELL_UNKNOWN])
            if len(splits[CELL_EMPTY]) == 6: # container is already solved?
                sets.update(splits[CELL_UNKNOWN])
        # having gone through all containers, we can apply the sets and clears
        for x,y in clears:
            self.clear_cell(x,y)
            made_progress = True
        for x,y in sets:
            self.set_cell_mine(x,y)
            made_progress = True
        return made_progress
    
    
    def rule_easy_clue_completion(self):
        empties = set()
        sets = set()
        for y in range(9):
            for x in range(9):
                cell = self.board[x, y]
                if cell.clue is None:
                    continue
                # Tally neighbors
                neighbor_coords = self.get_neighbor_coords(x, y)
                splits = self.split_cells_by_value(neighbor_coords)
                n_unknown = len(splits[CELL_UNKNOWN])
                # n_empty = len(splits[CELL_EMPTY])
                n_mine = len(splits[CELL_MINE])
                clue = cell.clue
                if n_unknown == 0:
                    continue
                if n_mine == clue:
                    empties.update(splits[CELL_UNKNOWN])
                if n_mine + n_unknown == clue:
                    sets.update(splits[CELL_UNKNOWN])
        made_progress = False
        for x, y in empties:
            self.clear_cell(x, y)
            made_progress = True
        for x, y in sets:
            self.set_cell_mine(x, y)
            made_progress = True
        return made_progress
        # todo...
        return False
    
    def rule_easy_greedy_clues(self):
        # todo...
        clears = set()
        for y in range(9):
            for x in range(9):
                cell = self.board[x, y]
                if cell.clue is None:
                    continue

                neighbor_coords = self.get_neighbor_coords(x, y)
                splits = self.split_cells_by_value(neighbor_coords)
                n_unknown = len(splits[CELL_UNKNOWN])
                n_mine = len(splits[CELL_MINE])
                if n_unknown == 0:
                    continue
                # get a list of container_ids that contain a neighbor of this cell
                enclosed_container_ids = []
                for cid,cont in enumerate(self.containers):
                    if all(coord in cont for coord in splits[CELL_UNKNOWN]):
                        enclosed_container_ids.append(cid)
                # print(f"checking clue {cell.x=} {cell.y=} {cell.clue=} {n_mine=} {n_unknown=} {enclosed_container_ids=} {splits[CELL_UNKNOWN]=}")
                for cid in enclosed_container_ids:
                    # print(f"singleton container found {cell.x=} {cell.y=} {cell.clue=} {n_mine=} {n_unknown=}")
                    if (cell.clue-n_mine) == 3:
                        for x,y in self.containers[cid]:
                            if (x,y) not in neighbor_coords and self.board[x,y].value == CELL_UNKNOWN:
                                clears.add((x,y))
        made_progress = False
        for x,y in clears:
            self.clear_cell(x,y)
            made_progress = True
        return made_progress

            
    def __str__(self):
        return self.puzzle_str

production_rules = [{'score':1, 'nom':'container-completion', 'function':PuzzleBoard.rule_easy_container_completion},
                    {'score':1, 'nom':'clue-completion', 'function':PuzzleBoard.rule_easy_clue_completion},
                    {'score':2, 'nom':'greedy-clues', 'function':PuzzleBoard.rule_easy_greedy_clues}, # STILL BUGGY
                    ]

from draw_limesudoku import draw_puzzle
step_counter = 0
puzzle_number = 0

def draw_solve_step(board, annotation=None):
    global step_counter, puzzle_number
    step_counter += 1

    solution_str = board.solution_string_found()
    # print(f"drawing {board.puzzle_str=} {solution_str=} {annotation=}")
    draw_puzzle(f"drawings/steps_{puzzle_number}_{step_counter}.png", board.puzzle_str, solution_str, annotation=f"Puzzle #{step_counter} {annotation}")

def solve(puzzle_str, known_answer_str=None, rand_seed = 1, max_solutions = 2, 
          layout='AAABBBCCCAAABBBCCCAAABBBCCCDDDEEEFFFDDDEEEFFFDDDEEEFFFGGGHHHIIIGGGHHHIIIGGGHHHIII',
          draw_steps=False):
    global puzzle_number
    puzzle_number += 1
    board = PuzzleBoard(puzzle_str, known_answer_str, layout=layout)
    try:
        solution_found = False
        work = 0
        last_rule_used = None
        while True:
            if board.solution_found():
                solution_found = True
                break
            made_progress = False
            for rule in production_rules:
                # print(f"checking rule {rule['nom']}")
                if rule['function'](board):
                    made_progress = True
                    work += rule['score']
                    last_rule_used = rule['nom']
                    break
            if draw_steps:
                draw_solve_step(board, annotation=last_rule_used)
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
        import traceback
        traceback.print_exc()
        return False,{}

    assert False # should never get here


if __name__ == '__main__':
    puzzle_str = '..32.......3...........1......3....4......4.2......43..3..................33..1..' # easy
    puzzle_str = '1..11..32.............3..332.33.23.32...3....2..3.33323.333..21.......3.1...22.21' # ridiculously easy
    solution,stats = solve(puzzle_str)
    print(f'{solution=} {stats=}')
