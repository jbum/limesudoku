# solve_PR.py
#
# PRODUCTION RULE solver for Minesweeper Sudoku
import sys

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
        self.neighbor_coords = self.get_neighbor_coords(x, y)
        self.id = f"{x},{y}"
        if value_str in '0123456789':
            self.clue = int(value_str)
            self.value = CELL_EMPTY
        elif value_str == 'O':
            self.clue = None
            self.value = CELL_MINE

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
    
    def __str__(self):
        return f"clue @ {chr(ord('A') + self.x)}{self.y+1} {self.clue=} {self.value=} {self.known_value=}"


K_DEFAULT_LAYOUT = 'AAABBBCCCAAABBBCCCAAABBBCCCDDDEEEFFFDDDEEEFFFDDDEEEFFFGGGHHHIIIGGGHHHIIIGGGHHHIII'

class PuzzleBoard:
    def __init__(self, puzzle_str, known_answer_str=None, 
                 layout=K_DEFAULT_LAYOUT,
                 verbose=False):
        
        if layout is None:
            layout = K_DEFAULT_LAYOUT

        self.puzzle_str = puzzle_str
        self.known_answer_str = puzzle_str
        self.layout = layout
        self.board = {}
        self.gw = 9
        self.gh = 9
        self.area = self.gw * self.gh
        self.verbose = verbose
        self.clue_addresses = []
        self.max_subgroup_split_depth = 0

        for i in range(self.area):
            x,y = i % self.gw, i // self.gw
            self.board[x,y] = Cell(x,y, puzzle_str[i])
            if known_answer_str:
                self.board[x,y].known_value = CELL_MINE if known_answer_str[i] == 'O' else CELL_EMPTY
            if self.board[x,y].clue is not None:
                self.clue_addresses.append((x,y))

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
        if self.board[x,y].value == CELL_EMPTY:
            return False
        if self.board[x,y].known_value is not None:
            if self.board[x,y].known_value != CELL_EMPTY:
                raise Exception(f'mismatched clear: x={x} y={y} {self.board[x,y].known_value=} rule {why=}')
        self.board[x,y].value = CELL_EMPTY
        return True

    def set_cell_mine(self, x, y, why='generic_reason'):
        if self.board[x,y].value == CELL_MINE:
            return False
        if self.board[x,y].known_value is not None:
            if self.board[x,y].known_value != CELL_MINE:
                raise Exception(f'mismatched set: x={x} y={y} {self.board[x,y].known_value}= rule {why=}')
        self.board[x,y].value = CELL_MINE
        return True

    def split_cells_by_value(self, cont):
        tallies = [[],[],[]]
        for x,y in cont:
            cell = self.board[x,y]
            tallies[cell.value].append((x,y))
        return tallies

    # def get_neighbor_coords(self, x, y):
    #     neighbor_coords = []
    #     for dx in [-1, 0, 1]:
    #         for dy in [-1, 0, 1]:
    #             if dx == 0 and dy == 0:
    #                 continue
    #             nx, ny = x + dx, y + dy
    #             if 0 <= nx < 9 and 0 <= ny < 9:
    #                 neighbor_coords.append((nx, ny))
    #     return neighbor_coords

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

    def unsolved_containers(self):
        for cont in self.containers:
            splits = self.split_cells_by_value(cont)
            if len(splits[CELL_UNKNOWN]) > 0:
                yield cont, splits

    def unsolved_clues(self):
        for x,y in self.clue_addresses:
            cell = self.board[x, y]
            neighbor_coords = cell.neighbor_coords
            splits = self.split_cells_by_value(neighbor_coords)
            if len(splits[CELL_UNKNOWN]) > 0:
                yield cell,splits

    def rule_easy_container_completion(self):
        immediate = False # immediate testing mode, leave this off, solves in fewer steps, but solving order will be less sensible
        made_progress = False
        clears = set()
        sets = set()
        for _,splits in self.unsolved_containers():
            if len(splits[CELL_MINE]) == 3: # container is already solved?
                clears.update(splits[CELL_UNKNOWN])
                if immediate:
                    for x,y in splits[CELL_UNKNOWN]:
                        made_progress = self.clear_cell(x,y) or made_progress
            if len(splits[CELL_EMPTY]) == 6: # container is already solved?
                sets.update(splits[CELL_UNKNOWN])
                if immediate:
                    for x,y in splits[CELL_UNKNOWN]:
                        made_progress = self.set_cell_mine(x,y) or made_progress
        # having gone through all containers, we can apply the sets and clears
        for x,y in clears:
            made_progress = self.clear_cell(x,y) or made_progress
        for x,y in sets:
            made_progress = self.set_cell_mine(x,y) or made_progress
        return made_progress
    
    
    def rule_easy_clue_completion(self):
        empties = set()
        sets = set()
        for cell,splits in self.unsolved_clues():
            # Tally neighbors
            n_unknown = len(splits[CELL_UNKNOWN])
            if len(splits[CELL_MINE]) > cell.clue:
                # should never hapen
                raise Exception(f"rule_easy_clue_completion logic issue: {x=} {y=} {cell.clue=} {len(splits[CELL_MINE])=} {len(splits[CELL_UNKNOWN])=}")
            n_mine = len(splits[CELL_MINE])
            clue = cell.clue
            if n_mine == clue:
                empties.update(splits[CELL_UNKNOWN])
            if n_mine + n_unknown == clue:
                sets.update(splits[CELL_UNKNOWN])
        made_progress = False
        for x, y in empties:
            made_progress = self.clear_cell(x, y) or made_progress
        for x, y in sets:
            made_progress = self.set_cell_mine(x, y) or made_progress
        return made_progress
        # todo...
        return False
    
    def rule_med_greedy_clues(self):
        # todo...
        clears = set()
        for cell,splits in self.unsolved_clues():
            n_mine = len(splits[CELL_MINE])
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
                        if (x,y) not in cell.neighbor_coords and self.board[x,y].value == CELL_UNKNOWN:
                            clears.add((x,y))
            # in a more generalized version, we could look for not-fully-enclosed clues that have a limit to their #external mines
            # that force minimum mine usage in each partially enclosed container, such as a 5

        made_progress = False
        for x,y in clears:
            made_progress = self.clear_cell(x,y) or made_progress
        return made_progress

    def rule_med_greedy_clues_general(self):
        """
        This covers sitation, where a 5 clue straddles just two disjoint containers (A,B), A has 3+ neighbors, and B has 2 neighbors.
        The two neighors in B are forced mines, and the remaining 3 mines must go in cell A as neighbors, so we can eliminate other unknowns in cell A.

        More generally stated
        This covers sitation, where a 4+ clue straddles just two disjoint containers (A,B), A has 3+ neighbors, 
        and B has (clue-3) neighbors.
        The unknown neighbors in B are forced mines, and the remaining clue-3 mines must go in cell A as neighbors, so we can eliminate other unknowns in cell A.

        This is a generalization of the rule_med_greedy_clues rule, which handles 4s and 5s instead of just 3s.

        """
        # todo...
        # if self.verbose:
        #     print(f"\n\nrule_med_greedy_clues_general")
        clears = set()
        sets = set()
        for cell,splits in self.unsolved_clues():
            if cell.clue < 4:
                continue
            if len(splits[CELL_MINE]) > 0: # current code has logic errors if there are any mines
                continue
            if cell.clue-len(splits[CELL_MINE]) < 4:
                continue
            # get a list of all containers that contain an unknown neighbor of this cell
            containers_with_unknown_neighbors = []
            for cid,cont in enumerate(self.containers):
                if any(coord in cont for coord in splits[CELL_UNKNOWN]):
                    containers_with_unknown_neighbors.append(cid)
            from itertools import combinations
            for cid1,cid2 in combinations(containers_with_unknown_neighbors, 2):
                if cid1 == cid2:
                    continue
                cont1 = self.containers[cid1]
                cont2 = self.containers[cid2]
                # check that the clue is fully contained in both
                if any((coord not in cont1 and coord not in cont2) for coord in splits[CELL_UNKNOWN]):
                    # if self.verbose:
                    #     print(f"found external cell")
                    continue
                # check that the two containers are disjoint, as far as the clue goes
                if any((coord in cont1 and coord in cont2) for coord in splits[CELL_UNKNOWN]):
                    # if self.verbose:
                    #     print(f"containrs aren't disjoint")
                    continue
                # swap the two cids if the number of neighbor unknowns is greater in cont1 than cont2
                # we want cont1 to be the smaller, forcing container
                if len([coord for coord in splits[CELL_UNKNOWN] if coord in cont1]) > len([coord for coord in splits[CELL_UNKNOWN] if coord in cont2]):
                    cid1,cid2 = cid2,cid1
                    cont1,cont2 = cont2,cont1
                # check if either container is forcing (e.g. a 5 that has only 2 choices in cont2)
                unknowns_in_cont1 = [coord for coord in splits[CELL_UNKNOWN] if coord in cont1]
                unknowns_in_cont2 = [coord for coord in splits[CELL_UNKNOWN] if coord in cont2]
                if len(unknowns_in_cont1) == cell.clue - 3:
                    # it's a force
                    for x,y in unknowns_in_cont1:
                        sets.add((x,y))
                    for x,y in cont2:
                        if (x,y) not in unknowns_in_cont2 and self.board[x,y].value == CELL_UNKNOWN:
                            clears.add((x,y))

        made_progress = False
        for x,y in clears:
            made_progress = self.clear_cell(x,y) or made_progress
        for x,y in sets:
            made_progress = self.set_cell_mine(x,y) or made_progress
        return made_progress



    def rule_med_pushy_clues_step_1_only(self):
        """
        Sort of a complimentary rule to easy_greedy_clues -- if the clue is n, and there are external blanks
        # and the number of external mines + external blanks == 3-n
        # the external blanks must be set to mines
        # this applies even if the clue-neighbors are not all contained in the same container
        """


        sets = set()
        for cell,splits in self.unsolved_clues():
            # get a list of container_ids that contain a neighbor of this cell
            relevant_container_ids = []
            for cid,cont in enumerate(self.containers):
                if any(coord in cont for coord in splits[CELL_UNKNOWN]):
                    relevant_container_ids.append(cid)
            # print(f"checking clue {cell.x=} {cell.y=} {cell.clue=} {n_mine=} {n_unknown=} {enclosed_container_ids=} {splits[CELL_UNKNOWN]=}")
            for cid in relevant_container_ids:
                # print(f"singleton container found {cell.x=} {cell.y=} {cell.clue=} {n_mine=} {n_unknown=}")
                cont = self.containers[cid]
                external_cells = [(x,y) for x,y in cont if (x,y) not in neighbor_coords]
                splits2 = self.split_cells_by_value(external_cells)
                if len(splits2[CELL_UNKNOWN]) > 0 and len(splits2[CELL_MINE]) + len(splits2[CELL_UNKNOWN]) == 3 - cell.clue:
                    for x,y in splits2[CELL_UNKNOWN]:
                        sets.add((x,y))
        made_progress = False
        for x,y in sets:
            made_progress = self.set_cell_mine(x,y) or made_progress
        return made_progress


    def rule_med_pushy_clues(self):
        """
        Sort of a complimentary rule to easy_greedy_clues -- if the clue is n, and there are external blanks
        # and the number of external mines + external blanks == 3-n
        # the external blanks must be set to mines
        # this applies even if the clue-neighbors are not all contained in the same container

        Part 2 (corollary)
        when this happens, it implies that the in-container neighboring cells must contain all the clue's mines
        so we can clear the unknown-neighbors of the clue that are not in the container-of-interest

        """



        sets = set()
        clears = set() # part 2
        for cell,splits in self.unsolved_clues():
            # get a list of container_ids that contain a neighbor of this cell
            
            relevant_container_ids = []
            for cid,cont in enumerate(self.containers):
                if any(coord in cont for coord in splits[CELL_UNKNOWN]):
                    relevant_container_ids.append(cid)
            # print(f"checking clue {cell.x=} {cell.y=} {cell.clue=} {n_mine=} {n_unknown=} {enclosed_container_ids=} {splits[CELL_UNKNOWN]=}")
            for cid in relevant_container_ids:
                # print(f"singleton container found {cell.x=} {cell.y=} {cell.clue=} {n_mine=} {n_unknown=}")
                cont = self.containers[cid]
                external_cells = [(x,y) for x,y in cont if (x,y) not in cell.neighbor_coords]
                splits2 = self.split_cells_by_value(external_cells)
                if len(splits2[CELL_UNKNOWN]) > 0 and len(splits2[CELL_MINE]) + len(splits2[CELL_UNKNOWN]) == 3 - cell.clue:
                    for x,y in splits2[CELL_UNKNOWN]:
                        sets.add((x,y))
                    # part 2 addition here
                    for x,y in splits[CELL_UNKNOWN]:
                        if (x,y) not in cont:
                            clears.add((x,y))
        made_progress = False
        for x,y in sets:
            made_progress = self.set_cell_mine(x,y) or made_progress
        for x,y in clears: # part 2
            made_progress = self.clear_cell(x,y) or made_progress
        return made_progress

    def rule_med_at_most_1_containers(self):
        """ Rule of at-most-1 containers.  
        If a container contains an at-most-1 group, and the #remaining-open-cells in that 
        container are equal to (3 - container.known.mines - 1), then we can set the remaining 
        open cells in the container to mines.
        """
        sets = set()
        for ci1,(cont1,splits1) in enumerate(self.unsolved_containers()):
            at_most_1_groups = set()
            for ci2,(cont2,splits2) in enumerate(self.unsolved_containers()):
                if ci1 == ci2:
                    continue
                if len(splits2[CELL_MINE]) == 2:
                    at_most_1_cells = [addr for addr in splits2[CELL_UNKNOWN] if addr in splits1[CELL_UNKNOWN]]
                    if len(at_most_1_cells) > 1:
                        at_most_1_groups.add(tuple(at_most_1_cells))
            # now similar check with clues with 1 remaining mine to go
            for cell,splits2 in self.unsolved_clues():
                if cell.clue - len(splits2[CELL_MINE]) == 1:
                    at_most_1_cells = [addr for addr in splits2[CELL_UNKNOWN] if addr in splits1[CELL_UNKNOWN]]
                    if len(at_most_1_cells) > 1:
                        at_most_1_groups.add(tuple(at_most_1_cells))

            for at_most_1_group in at_most_1_groups:
                if len(splits1[CELL_UNKNOWN]) - len(at_most_1_group) == 3 - len(splits1[CELL_MINE]) - 1:
                    for x,y in splits1[CELL_UNKNOWN]:
                        if (x,y) not in at_most_1_group:    
                            sets.add((x,y))

        made_progress = False
        for x,y in sets:
            made_progress = self.set_cell_mine(x,y) or made_progress
        return made_progress

    def rule_med_at_most_1_clues(self):
        """ Rule of at-most-1 containers.  
        If a clue contains an at-most-1 group (due to interactions with containers or other clues), 
        and the #remaining-open-cells in that clue are equal to 
        (clue# - clue.known.mines - 1), 
        then we can set the remaining open cells in the clue to mines.
        """
        sets = set()
        for cell,splits1 in self.unsolved_clues():
            at_most_1_groups = set()
            for cont2 in self.containers:
                splits2 = self.split_cells_by_value(cont2)
                if len(splits2[CELL_MINE]) == 2:
                    at_most_1_cells = [addr for addr in splits2[CELL_UNKNOWN] if addr in splits1[CELL_UNKNOWN]]
                    if len(at_most_1_cells) > 1:
                        at_most_1_groups.add(tuple(at_most_1_cells))
            # now similar check with clues with 1 remaining mine to go
            for cell2,splits2 in self.unsolved_clues():
                if cell.id == cell2.id:
                    continue
                if cell2.clue - len(splits2[CELL_MINE]) == 1:
                    at_most_1_cells = [addr for addr in splits2[CELL_UNKNOWN] if addr in splits1[CELL_UNKNOWN]]
                    if len(at_most_1_cells) > 1:
                        at_most_1_groups.add(tuple(at_most_1_cells))

            for at_most_1_group in at_most_1_groups:
                if len(splits1[CELL_UNKNOWN]) - len(at_most_1_group) == cell.clue - len(splits1[CELL_MINE]) - 1:
                    for x,y in splits1[CELL_UNKNOWN]:
                        if (x,y) not in at_most_1_group:    
                            sets.add((x,y))

        made_progress = False
        for x,y in sets:
            made_progress = self.set_cell_mine(x,y) or made_progress
        return made_progress
    
    def address_to_nom(self, x, y):
        return f"{chr(ord('A') + x)}{y+1}"

    def rule_med_at_least_1_clues_with_debugging(self):
        """ Rule of at-most-1 containers.  
        If a clue contains an entire at-least-1 group that would finish the clue, then
        the remaining unknown neighbors (not in that group) can be cleared.
        """
        if self.verbose:
            print(f"rule_med_at_least_1_clues")
        clears = set()
        for cell,splits1 in self.unsolved_clues():
            if self.verbose:
                print(f"\nLooking at clue {self.address_to_nom(cell.x,cell.y)} {cell.clue=} {len(splits1[CELL_MINE])=} {len(splits1[CELL_UNKNOWN])=}")

            # don't bother unless clue needs just 1 more mien
            if cell.clue > 1 + len(splits1[CELL_MINE]):
                continue
            at_least_1_groups = set()
            for ci2, cont2 in enumerate(self.containers):
                splits2 = self.split_cells_by_value(cont2)
                if len(splits2[CELL_MINE]) == 2:
                    if self.verbose:
                        print(f"Container {ci2} is interesting")
                    at_least_1_cells = [addr for addr in splits2[CELL_UNKNOWN] if addr in splits1[CELL_UNKNOWN]]
                    if len(at_least_1_cells) > 0 and len(at_least_1_cells) == len(splits2[CELL_UNKNOWN]):
                        if self.verbose:
                            print(f"{len(at_least_1_cells)} cells added")
                        at_least_1_groups.add(tuple(at_least_1_cells))
            # now similar check with clues with 1 remaining mine to go
            for cell2,splits2 in self.unsolved_clues():
                if cell.id == cell2.id:
                    continue
                if cell2.clue - len(splits2[CELL_MINE]) == 1:
                    at_least_1_cells = [addr for addr in splits2[CELL_UNKNOWN] if addr in splits1[CELL_UNKNOWN]]
                    if len(at_least_1_cells) > 0 and len(at_least_1_cells) == splits2[CELL_UNKNOWN]:
                        at_least_1_groups.add(tuple(at_least_1_cells))


            for at_least_1_group in at_least_1_groups:
                for x,y in splits1[CELL_UNKNOWN]:
                    if (x,y) not in at_least_1_group:    
                        clears.add((x,y))

    def rule_med_at_least_1_clues(self):
        """ Rule of at-most-1 containers.  
        If a clue contains an entire at-least-1 group that would finish the clue, then
        the remaining unknown neighbors (not in that group) can be cleared.
        """
        clears = set()
        for cell,splits1 in self.unsolved_clues():
            # don't bother unless clue needs just 1 more mine
            if cell.clue > 1 + len(splits1[CELL_MINE]):
                continue
            at_least_1_groups = set()
            for cont2,splits2 in self.unsolved_containers():
                if len(splits2[CELL_MINE]) == 2:
                    at_least_1_cells = [addr for addr in splits2[CELL_UNKNOWN] if addr in splits1[CELL_UNKNOWN]]
                    if len(at_least_1_cells) > 0 and len(at_least_1_cells) == len(splits1[CELL_UNKNOWN]):
                        at_least_1_groups.add(tuple(at_least_1_cells))
            # now similar check with clues with 1 remaining mine to go
            for cell2,splits2 in self.unsolved_clues():
                if cell.id == cell2.id:
                    continue
                if cell2.clue - len(splits2[CELL_MINE]) == 1:
                    at_least_1_cells = [addr for addr in splits2[CELL_UNKNOWN] if addr in splits1[CELL_UNKNOWN]]
                    if len(at_least_1_cells) > 0 and len(at_least_1_cells) == splits2[CELL_UNKNOWN]:
                        at_least_1_groups.add(tuple(at_least_1_cells))

            # check for containers that fully contain the at-least-one group.
            for at_least_1_group in at_least_1_groups:
                # if self.verbose:
                #     print(f"at-least-1-group: {at_least_1_group}")
                for x,y in splits1[CELL_UNKNOWN]:
                    if (x,y) not in at_least_1_group:    
                        clears.add((x,y))
                # check for containers it is fully contained in, if they exist, use the group to clear the other cells in container
                for cont in self.containers:
                    if all(coord in cont for coord in at_least_1_group):
                        cont_splits = self.split_cells_by_value(cont)
                        if len(cont_splits[CELL_MINE]) == 2:    
                            for x,y in cont_splits[CELL_UNKNOWN]:
                                if (x,y) not in at_least_1_group:
                                    clears.add((x,y))

            for cont,splits in self.unsolved_containers():
                if len(splits[CELL_MINE]) == 2:
                    at_least_1_cells = [addr for addr in splits[CELL_UNKNOWN] if addr in splits1[CELL_UNKNOWN]]


        made_progress = False
        for x,y in clears:
            made_progress = self.clear_cell(x,y) or made_progress
        return made_progress

    def __str__(self):
        return self.puzzle_str
    
    def address_list(self, cell_list):
        return [self.address_to_nom(x,y) for x,y in sorted(list(cell_list))]



    """
    A subgroup consists of a set of cells, an order value, and a kind (at-least or at-most)
    We can use to indicate a group of cells contains 'at least 2 mines' or 'at most 2 mines'
    An optional 'source' string is used to identify the source of the subgroup.
    """
    def group_to_string(self, group):
        return f"{group['kind']}-{group['ord']}: {self.address_list(group['cells'])} ({group['source']})"

    def group_to_key(self, group):
        key = f"{group['kind']}-{group['ord']}-{self.address_list(group['cells'])}"
        # print(f"group_to_key: {key}")
        return key

    def init_subgroups(self):
        self.sub_groups = [] # used to store the subgroups
        self.group_keys = set() # used to insure uniqueness

    def add_subgroup(self, group):
        key = self.group_to_key(group)
        
        if key not in self.group_keys:
            self.group_keys.add(key)
            self.sub_groups.append(group)
            return True
        return False
    
    def at_least_groups(self):
        for group in self.sub_groups:
            if group['kind'] == 'at-least':
                yield group
    
    def at_most_groups(self):
        for group in self.sub_groups:
            if group['kind'] == 'at-most':
                yield group


    def list_available_groups(self, label):
        if (self.verbose):
            print(f"\n{label}:")
            for group in self.sub_groups:
                print(f"{self.group_to_string(group)}")
                # check if this is valid
                known_mines = sum([1 for x,y in group['cells'] if self.board[x,y].known_value == CELL_MINE])
                if group['kind'] == 'at-least' and known_mines < group['ord']:
                    print(f"invalid at-least-{group['ord']}")
                    sys.exit(1)
                if group['kind'] == 'at-most' and known_mines > group['ord']:
                    print(f"invalid at-most-{group['ord']}")
                    sys.exit(1)


    def rule_hard_subgroups(self):
        """
        This is an expensive rule that is used to solve the harder puzzles.  It basically involves identifying the interactions between
        at-least-N and at-most-N groups, and using them to make progress.
        """
        if self.verbose:
            print(f"\n\nrule_hard_subgroups")
        clears = set()
        sets = set()
        self.init_subgroups()
        # walk through the containers and collect groups of 1 and 2
        for cont,splits in self.unsolved_containers():
            splits = self.split_cells_by_value(cont)
            ord = 3 - len(splits[CELL_MINE])
            self.add_subgroup({'ord':ord, 'cells':splits[CELL_UNKNOWN], 'source':f'container', 'kind':'at-least', 'split_depth':0})
            self.add_subgroup({'ord':ord, 'cells':splits[CELL_UNKNOWN], 'source':f'container', 'kind':'at-most', 'split_depth':0})

        # self.list_available_groups("CONTAINERS")

        # walk through the clues and collect groups of 1 and 2
        for cell,splits in self.unsolved_clues():
            rem_cells = cell.clue-len(splits[CELL_MINE])
            self.add_subgroup({'ord':rem_cells, 'cells':splits[CELL_UNKNOWN], 'source':f'clue {self.address_to_nom(cell.x,cell.y)}:{cell.clue}', 'kind':'at-least', 'split_depth':0})
            self.add_subgroup({'ord':rem_cells, 'cells':splits[CELL_UNKNOWN], 'source':f'clue {self.address_to_nom(cell.x,cell.y)}:{cell.clue}', 'kind':'at-most', 'split_depth':0})

        # self.list_available_groups(at_least_groups, at_most_groups, "CLUES")

        # SUBDIVISION - use keys to keep track of the subgroups, loop on this subdivision until we can make no progress
        # we want to try simple subdivisions first, before recursing, which makes the logic increasingly complex
        # this also speeds up solves
        # maximum split depth is about 7 at the moment
        made_subdivisions_progress = True
        while made_subdivisions_progress and len(clears) == 0 and len(sets) == 0:
            made_subdivisions_progress = False

            # process the groups to make more groups...
            # a clue which has a subset of neighbors that are part of an at-most-N 
            # has it’s remaining numbers in an at-least-(clue-mines-N) (and vice versa)
            for group in self.at_most_groups():
                # if a subset of clue's unknowns intersect this group, then set the remaining nebs of the clue to the compliment
                for cell,splits in self.unsolved_clues():
                    intersection = set(splits[CELL_UNKNOWN]) & set(group['cells'])
                    proposed_value = (cell.clue-len(splits[CELL_MINE])) - group['ord']
                    proposed_cells = list(set(splits[CELL_UNKNOWN]) - intersection)
                    if len(intersection) > 0 and len(intersection) < len(splits[CELL_UNKNOWN]) and proposed_value > 0:
                        new_group = {'ord':proposed_value, 
                                    'cells':proposed_cells, 
                                    'source':f'clue {self.address_to_nom(cell.x,cell.y)}:{cell.clue} split subset of {group["source"]}',
                                    'kind':'at-least',
                                    'split_depth':group['split_depth']+1}
                        made_subdivisions_progress = self.add_subgroup(new_group) or made_subdivisions_progress
            # # and vice versa !!!
            for group in self.at_least_groups():
                # if a subset of clue's unknowns intersect this group, then set the remaining nebs of the clue to the compliment
                for cell,splits in self.unsolved_clues():
                    if not all(coord in splits[CELL_UNKNOWN] for coord in group['cells']):
                        continue
                    intersection = set(splits[CELL_UNKNOWN]) & set(group['cells'])
                    proposed_value = (cell.clue-len(splits[CELL_MINE])) - group['ord']
                    proposed_cells = list(set(splits[CELL_UNKNOWN]) - intersection)
                    if len(intersection) > 0 and len(intersection) < len(splits[CELL_UNKNOWN]) and proposed_value > 0 and proposed_value < len(proposed_cells):
                        new_group = {'ord':proposed_value, 
                                    'cells':proposed_cells, 
                                    'source':f'clue {self.address_to_nom(cell.x,cell.y)}:{cell.clue} split subset of {group["source"]}',
                                    'kind':'at-most',
                                    'split_depth':group['split_depth']+1}
                        made_subdivisions_progress = self.add_subgroup(new_group) or made_subdivisions_progress

            # an at-least-N that is a full subset of an at-most-N+ (V) forces the remainder cells to at-most-(V-N)
            for group_atleast in self.at_least_groups(): # inner
                for group_atmost in self.at_most_groups(): # outer
                    if group_atleast['ord'] < group_atmost['ord']:
                        if all(coord in group_atmost['cells'] for coord in group_atleast['cells']):
                            remainder = set(group_atmost['cells']) - set(group_atleast['cells'])
                            proposed_value = group_atmost['ord'] - group_atleast['ord']
                            proposed_cells = list(remainder)
                            if len(remainder) > 0 and proposed_value > 0 and proposed_value < len(proposed_cells):
                                new_group = {'ord':proposed_value, 
                                            'cells':proposed_cells, 
                                            'source':f'insersection of {self.group_to_string(group_atleast)} and {self.group_to_string(group_atmost)}',
                                            'kind':'at-most',
                                            'split_depth':max(group_atleast['split_depth'], group_atmost['split_depth'])+1}
                                made_subdivisions_progress = self.add_subgroup(new_group) or made_subdivisions_progress

        

            # # an at-least fully inside an at-least of lower order, pushes it's order up - not effective
            # for group_atleast in self.at_least_groups(): # inner
            #     for group_atleast2 in at_least_groups: # outer
            #         if group_atleast['ord'] > group_atleast2['ord']:
            #             if all(coord in group_atleast2['cells'] for coord in group_atleast['cells']):
            #                 group_atleast2['ord'] = group_atleast['ord']
            #                 made_subdivisions_progress = self.add_subgroup(group_atleast2) or made_subdivisions_progress


            # # an at-most inside an at-most of lesser value can have it's value reduced - not effective
            # for group_atmost in self.at_most_groups(): # inner
            #     for group_atmost2 in self.at_most_groups(): # outer
            #         if group_atmost['ord'] > group_atmost2['ord']:
            #             if all(coord in group_atmost2['cells'] for coord in group_atmost['cells']):
            #                 group_atmost['ord'] = group_atmost2['ord']
            #                 made_subdivisions_progress = self.add_subgroup(group_atmost) or made_subdivisions_progress

            # an at-most that is inside an at-least of greater order, makes the remainder at-least (outer.ord-inner.ord)
            for group_atmost in self.at_most_groups(): # inner
                for group_atleast in self.at_least_groups(): # outer
                    if group_atleast['ord'] > group_atmost['ord']:
                        if all(coord in group_atleast['cells'] for coord in group_atmost['cells']): # is it full contained?
                            remainder = set(group_atleast['cells']) - set(group_atmost['cells']) # should be [d9]
                            proposed_value = group_atleast['ord'] - group_atmost['ord'] # should be 1
                            proposed_cells = list(remainder)
                            if len(remainder) > 0 and proposed_value > 0:
                                new_group = {'ord':proposed_value, 
                                            'cells':proposed_cells, 
                                            'source':f'insersection of {self.group_to_string(group_atleast)} and {self.group_to_string(group_atmost)}',
                                            'kind':'at-least',
                                            'split_depth':max(group_atleast['split_depth'], group_atmost['split_depth'])+1}
                                made_subdivisions_progress = self.add_subgroup(new_group) or made_subdivisions_progress

            # # if a clue is part of disjoint at-least-N and at-least-M, and N+M = clue-mines, then the two subsets are at-most-N, at-most-M
            # # currently bugged
            # for group_1 in self.at_least_groups(): # inner
            #     for group_2 in self.at_least_groups(): # outer
            #         # if they overlap at all, continue
            #         if any(coord in group_2['cells'] for coord in group_1['cells']):
            #             continue
            #         for cell,splits in self.unsolved_clues():
            #             if cell.clue-len(splits[CELL_MINE]) != group_1['ord'] + group_2['ord']:
            #                 continue
            #             intersection_1 = set(splits[CELL_UNKNOWN]) & set(group_1['cells'])
            #             if len(intersection_1) == 0:
            #                 continue
            #             intersection_2 = set(splits[CELL_UNKNOWN]) & set(group_2['cells'])
            #             if len(intersection_2) == 0:
            #                 continue
            #             for group,intersection in [(group_1, intersection_1), (group_2, intersection_2)]:
            #                 new_group = {'ord':group['ord'], 
            #                              'cells':list(intersection),
            #                              'source':f'disjoint split',
            #                              'kind':'at-most',
            #                              'split_depth':max(group_1['split_depth'], group_2['split_depth'])+1}
            #                 made_subdivisions_progress = self.add_subgroup(new_group) or made_subdivisions_progress

            # END SUBDIVISION/MUTATIONS HERE...

            self.list_available_groups("CLUES SPLITS")

            # An at-least-N that is a full subset of an at-most-N (same n), empties the intersection of the two sets.
            for group_atleast in self.at_least_groups():
                for group_atmost in self.at_most_groups():
                    if group_atleast['ord'] == group_atmost['ord']:
                        if all(coord in group_atmost['cells'] for coord in group_atleast['cells']):
                            remainder = set(group_atmost['cells']) - set(group_atleast['cells'])
                            if len(remainder) > 0:
                                if self.verbose:
                                    print(f"clearing {self.address_list(remainder)} from {self.group_to_string(group_atleast)} inside {self.group_to_string(group_atmost)}")
                                clears.update(remainder)
                                self.max_subgroup_split_depth = max(self.max_subgroup_split_depth, group_atleast['split_depth'])
                                self.max_subgroup_split_depth = max(self.max_subgroup_split_depth, group_atmost['split_depth'])

            if self.verbose:
                print("DONE CLEARANCE CHECKS")

            # an at-least-2 contains an at-most-1, and there is one remaining cell, we can place it.

            # an at-least-N group that has a length of N can be set to mines
            for group in self.at_least_groups():
                if len(group['cells']) == group['ord']:
                    for x,y in group['cells']:
                        sets.add((x,y))
                        self.max_subgroup_split_depth = max(self.max_subgroup_split_depth, group['split_depth'])

        # apply other at-least/-most patterns
        made_progress = False
        for x,y in clears:
            made_progress = self.clear_cell(x,y) or made_progress
        for x,y in sets:
            made_progress = self.set_cell_mine(x,y) or made_progress
        return made_progress



production_rules = [{'score':1, 'tier':1, 'nom':'container-completion', 'function':PuzzleBoard.rule_easy_container_completion},
                    {'score':1, 'tier':1, 'nom':'clue-completion', 'function':PuzzleBoard.rule_easy_clue_completion},
                    {'score':2, 'tier':2, 'nom':'greedy-clues', 'function':PuzzleBoard.rule_med_greedy_clues},
                    {'score':2, 'tier':2, 'nom':'pushy-ones', 'function':PuzzleBoard.rule_med_pushy_clues},
                    {'score':3, 'tier':2, 'nom':'at-most-1-containers', 'function':PuzzleBoard.rule_med_at_most_1_containers},
                    {'score':3, 'tier':2, 'nom':'at-most-1-clues', 'function':PuzzleBoard.rule_med_at_most_1_clues},
                    {'score':3, 'tier':2, 'nom':'at-least-1-clues', 'function':PuzzleBoard.rule_med_at_least_1_clues},
                    {'score':5, 'tier':3, 'nom':'hard-subgroups', 'function':PuzzleBoard.rule_hard_subgroups},
                    ]

from draw_limesudoku import draw_puzzle
step_counter = 0
puzzle_number = 0

def draw_solve_step(board, annotation=None):
    global step_counter, puzzle_number
    step_counter += 1

    solution_str = board.solution_string_found()
    # print(f"drawing {board.puzzle_str=} {solution_str=} {annotation=}")
    draw_puzzle(f"drawings/steps_{puzzle_number:03d}_{step_counter:03d}.png", board.puzzle_str, solution_str, annotation=f"Puzzle #{step_counter} {annotation}")

default_options = {
    'max_tier': None,
    'draw_steps': False,
    'verbose': False,
    'layout': 'AAABBBCCCAAABBBCCCAAABBBCCCDDDEEEFFFDDDEEEFFFDDDEEEFFFGGGHHHIIIGGGHHHIIIGGGHHHIII',
    'rand_seed': 1,
    'draw_unsolved': False,
    'nom': 'untitled-puzzle',
    'ptype': 'lime'
}

def solve(puzzle_str, known_answer_str=None, options = {}):

    myoptions = default_options.copy()
    myoptions.update(options)
    max_tier = myoptions['max_tier']
    draw_steps = myoptions['draw_steps']
    verbose = myoptions['verbose']
    layout = myoptions['layout']
    draw_unsolved = myoptions['draw_unsolved']
    nom = myoptions['nom']
    ptype = myoptions['ptype']
    max_tier_encountered = 0

    # # unused params
    # rand_seed = options['rand_seed']
    # max_solutions = options['max_solutions']


    global puzzle_number
    puzzle_number += 1
    board = PuzzleBoard(puzzle_str, known_answer_str, layout=layout, verbose=verbose)
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
                if max_tier is not None and rule['tier'] > max_tier:
                    continue
                if rule['function'](board):
                    made_progress = True
                    max_tier_encountered = max(max_tier_encountered, rule['tier'])
                    work += rule['score']
                    last_rule_used = rule['nom']
                    break
            if draw_steps:
                draw_solve_step(board, annotation=last_rule_used+" "+str(board.max_subgroup_split_depth) if made_progress else "no progress")
            if not made_progress:
                break
        if solution_found:
            sol_string_found = board.solution_string_found()
            if known_answer_str is not None and sol_string_found != known_answer_str:
                raise Exception(f'solution found but does not match known answer: {sol_string_found=} {known_answer_str=}')
        else:
            sol_string_found = "no solution"
            if draw_unsolved:
                partial_solution_str = board.solution_string_found()
                # print(f"drawing {board.puzzle_str=} {solution_str=} {annotation=}")
                draw_puzzle(f"drawings/unsolved_{nom}.png", board.puzzle_str, partial_solution_str, annotation=f"{nom} unsolved")
        return sol_string_found, {'work':work+10*board.max_subgroup_split_depth, 'mta':max_tier_encountered} # , 'mbsd':board.max_subgroup_split_depth}
    except Exception as e:
        print(f'PR Solve error: {e}')
        import traceback
        traceback.print_exc()
        return None,{}

    assert False # should never get here


if __name__ == '__main__':
    # puzzle_str = '..32.......3...........1......3....4......4.2......43..3..................33..1..' # easy
    puzzle_str = '1..11..32.............3..332.33.23.32...3....2..3.33323.333..21.......3.1...22.21' # ridiculously easy
    solution,stats = solve(puzzle_str)
    print(f'{solution=} {stats=}')
