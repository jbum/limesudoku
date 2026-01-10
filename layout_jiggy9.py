# jigsaw_maker
import random, sys, logging
import cairo

# hastily ported from my C code - not very python-idiomatic yet
attempts = 0
debug_draw = False
layout_draw_dir = 'layout_draw'
layout_draw_counter = 0
no_symmetry = False
sym_buckets = [0] * 5
draw_annotations = False

class JigsawMaker():
    def __init__(self, num_symbols):
        self.num_symbols = num_symbols
        self.num_squares = num_symbols * num_symbols # assumes square grid - may need to fix for samurai...


    def draw_layout(self, filename, annotation):
        tw = 20
        th = 20
        margin = 20
        puzzle_width = self.num_symbols*tw + 2*margin
        puzzle_height = self.num_symbols*th + 2*margin
        grid_width = self.num_symbols*tw
        grid_height = self.num_symbols*th

        region_colors = [
            (0.82, 0.93, 0.75),  # light pastel green
            (0.894, 0.102, 0.110), # red
            (0.216, 0.494, 0.722), # blue
            (0.302, 0.686, 0.290), # green
            (0.596, 0.306, 0.639), # purple
            (1.000, 0.498, 0.000), # orange
            (1.000, 1.000, 0.200), # yellow
            (0.651, 0.337, 0.157), # brown
            (0.969, 0.506, 0.749), # pink

            (0.121, 0.466, 0.705), # teal blue (replaces gray)
            (1.00, 0.90, 0.70),  # pastel tan
            (0.92, 0.93, 0.70),  # pastel olive
            (0.70, 0.93, 0.96),  # pastel cyan
            (0.93, 0.80, 0.93),  # pastel violet
            (1.00, 0.82, 0.77),  # pastel salmon
            (0.80, 0.80, 1.00),  # pastel cobalt
            (0.80, 0.90, 0.80),  # pastel moss
            (1.00, 0.72, 0.74),  # pastel coral
            (0.80, 0.95, 0.70),  # pastel lime
            (0.98, 0.85, 0.70)   # pastel earth
        ]
                
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, puzzle_width, puzzle_height)
        ctx = cairo.Context(surface)
        # Fill entire area with medium gray
        ctx.set_source_rgb(1, 1, 1)
        ctx.rectangle(0, 0, puzzle_width, puzzle_height)
        ctx.fill()

        ctx.save()
        ctx.translate(margin, margin)

        ctx.set_source_rgb(0.5, 0.5, 0.5)
        ctx.rectangle(0, 0, grid_width, grid_height)
        ctx.fill()

        # Draw black stroke rectangle around the entire area
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_line_width(2)
        ctx.rectangle(0, 0, grid_width, grid_height)
        ctx.stroke()

        # Save the transformation matrix and translate origin to (margin, margin)

        # Process each cell
        for y in range(self.num_symbols):
            for x in range(self.num_symbols):
                addr = y * self.num_symbols + x
                # Fill cell with white if it's not empty
                if self.cells[addr] != '.':
                    region_color_idx = (ord(self.cells[addr]) - ord('A')) % 20
                    ctx.set_source_rgb(*region_colors[region_color_idx])
                    ctx.rectangle(x*tw, y*th, tw, th)
                    ctx.fill()
                # Stroke right edge if different from right neighbor
                if x < self.num_symbols-1 and self.cells[addr] != self.cells[addr+1]:
                    ctx.set_source_rgb(0, 0, 0)
                    ctx.set_line_width(2)
                    ctx.move_to((x+1)*tw, y*th)
                    ctx.line_to((x+1)*tw, (y+1)*th)
                    ctx.stroke()
                # Stroke bottom edge if different from bottom neighbor
                if y < self.num_symbols-1 and self.cells[addr] != self.cells[addr + self.num_symbols]:
                    ctx.set_source_rgb(0, 0, 0)
                    ctx.set_line_width(2)
                    ctx.move_to(x*tw, (y+1)*th)
                    ctx.line_to((x+1)*tw, (y+1)*th)
                    ctx.stroke()
        ctx.restore()
        if annotation and draw_annotations:
            ctx.set_source_rgb(0, 0, 0)
            ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(18)
            ctx.move_to(margin, margin-2)
            ctx.show_text(annotation)
        surface.write_to_png(filename)

    def init_growth_fill(self):
        # should return cells
        r = random.randrange(100)
        if r < 50:
            self.symFlags = 4  # XY
        elif r < 75:
            self.symFlags = 0  # Asymmetry
        elif r < 95:
            self.symFlags = 1  # X
        else:
            self.symFlags = 2  # Y
        if no_symmetry:
            self.symFlags = 0 # force no symmetry for debugging
        # self.symFlags = 0
        # print("SYMMETRY",self.symFlags)
        self.cells = ['.'] * self.num_squares
        self.pairedColors = [-1] * self.num_symbols
        self.nbrUsed = [0] * self.num_symbols
        self.totUsed = 0
        self.regionCtr = 0

        if self.symFlags == 4:
            n = 0
            self.pairedColors[n] = n
            idx = 4*self.num_symbols + 4
            self.cells[idx] = chr(ord('A')+n)
            self.popJQueue(n)
        elif self.symFlags == 1 or self.symFlags == 2:
            for n in range(3):
                self.pairedColors[n] = n
                for i in range(3):
                    idx = (3*n+i)*self.num_symbols+4 if self.symFlags == 1 else 4*self.num_symbols+(3*n+i)
                    self.cells[idx] = chr(ord('A')+n)
                    self.popJQueue(n)

    def is_too_perfect_jigsaw_grid(self, cells):
        numBlocks = 0
        numRows = 0
        numCols = 0
        for y in range(0,self.num_symbols,3):
            for x in range(0,self.num_symbols,3):
                n = y*self.num_symbols + x
                if  cells[n] == cells[n+1] \
                and cells[n] == cells[n+2] \
                and cells[n] == cells[n+self.num_symbols] \
                and cells[n] == cells[n+self.num_symbols+1] \
                and cells[n] == cells[n+self.num_symbols+2] \
                and cells[n] == cells[n+self.num_symbols*2] \
                and cells[n] == cells[n+self.num_symbols*2+1] \
                and cells[n] == cells[n+self.num_symbols*2+2]:
                    numBlocks += 1
        if numBlocks > 1:
            return True

        for x in range(self.num_symbols):
            n = x
            if cells[n] == cells[n+self.num_symbols*1] \
            and cells[n] == cells[n+self.num_symbols*2] \
            and cells[n] == cells[n+self.num_symbols*3] \
            and cells[n] == cells[n+self.num_symbols*4] \
            and cells[n] == cells[n+self.num_symbols*5] \
            and cells[n] == cells[n+self.num_symbols*6] \
            and cells[n] == cells[n+self.num_symbols*7] \
            and cells[n] == cells[n+self.num_symbols*8]:
                numCols += 1
        if numCols > 1:
            return True

        for y in range(self.num_symbols):
            n = y*self.num_symbols
            if cells[n] == cells[n+1] \
            and cells[n] == cells[n+2] \
            and cells[n] == cells[n+3] \
            and cells[n] == cells[n+4] \
            and cells[n] == cells[n+5] \
            and cells[n] == cells[n+6] \
            and cells[n] == cells[n+7] \
            and cells[n] == cells[n+8]:
                numRows += 1
        if numRows > 1:
            return True

        return False

    def getCell(self, x,y):
        return self.cells[y * self.num_symbols + x]

    def isBridge(self, cells, idx):
        nMask = 0
        (cx,cy) = (idx % self.num_symbols, idx // self.num_symbols)
        cr = cells[idx]

        # make bitmask for neighboring connections
        if cx > 0 and cy > 0 and self.getCell(cx-1,cy-1) == cr:
            nMask |= 0x01
        if cy > 0 and self.getCell(cx,cy-1) == cr:
            nMask |= 0x02
        if cx < self.num_symbols-1 and cy > 0 and self.getCell(cx+1,cy-1) == cr:
            nMask |= 0x04
        if cx < self.num_symbols-1 and self.getCell(cx+1,cy) == cr:
            nMask |= 0x08
        if cx < self.num_symbols-1 and cy < self.num_symbols-1 and self.getCell(cx+1,cy+1) == cr:
            nMask |= 0x10
        if cy < self.num_symbols-1 and self.getCell(cx,cy+1) == cr:
            nMask |= 0x20
        if cx > 0 and cy < self.num_symbols-1 and self.getCell(cx-1,cy+1) == cr:
            nMask |= 0x40
        if cx > 0 and self.getCell(cx-1,cy) == cr:
            nMask |= 0x80

        res = nMask & 0xaa
        if res == 0x88 or res == 22:
            return True
        elif res == 0x0A:
            if ((nMask & 0x04) == 0):
                return True
        elif res == 0x28:
            if ((nMask & 0x10) == 0):
                return True
        elif res == 0xa0:
            if ((nMask & 0x40) == 0):
                return True
        elif res == 0x82:
            if ((nMask & 0x01) == 0):
                return True
        elif res == 0x8a:
            if ((nMask & 0x05) != 0x05):
                return True
        elif res == 0x2a:
            if ((nMask & 0x14) != 0x14):
                return True
        elif res == 0xa8:
            if ((nMask & 0x50) != 0x50):
                return True
        elif res == 0xa2:
            if ((nMask & 0x41) != 0x41):
                return True
        return False

    def isSelfReflexive(self, x, y):
        if self.symFlags == 0:
            return False
        x2 = (self.num_symbols-1)-x if (self.symFlags & 0x05) != 0 else x
        y2 = (self.num_symbols-1)-y if (self.symFlags & 0x06) != 0 else y
        return x2 == x and y2 == y

    def floodFill(self, cells, n):
        (x,y) = (n % self.num_symbols, n // self.num_symbols)
        r = cells[n]
        self.fills[n] = cells[n]
        self.fillSum += 1
        if x > 0 and self.fills[n-1] == 0 and cells[n-1] == r:
            self.floodFill(cells,n-1)
        if y > 0 and self.fills[n-self.num_symbols] == 0 and cells[n-self.num_symbols] == r:
            self.floodFill(cells,n-self.num_symbols)
        if x < self.num_symbols-1 and self.fills[n+1] == 0 and cells[n+1] == r:
            self.floodFill(cells,n+1)
        if y < self.num_symbols-1 and self.fills[n+self.num_symbols] == 0 and cells[n+self.num_symbols] == r:
            self.floodFill(cells,n+self.num_symbols)

    def floodFillCount(self, cells, n):
        self.fillSum = 0
        self.floodFill(cells, n)
        return self.fillSum

    def is_grid_legal(self, cells):
        # print("islegal",''.join(cells))
        rsums = [0] * self.num_symbols
        for n in range(self.num_squares):
            if cells[n] == 0 or ord(cells[n]) < ord('A') or ord(cells[n]) > ord('A')+self.num_symbols:
                return False
            rsums[ord(cells[n]) - ord('A')] += 1
        for i in range(self.num_symbols):
            if rsums[i] != self.num_symbols:
                return False
        # simple orphan check
        for n in range(self.num_squares):
            (x,y) = (n % self.num_symbols, n // self.num_symbols)
            r = cells[n]
            if x > 0 and ord(self.getCell(x-1,y)) == ord(r):
                continue
            if x < self.num_symbols-1 and ord(self.getCell(x+1,y)) == ord(r):
                continue
            if y > 0 and ord(self.getCell(x,y-1)) == ord(r):
                continue
            if y < self.num_symbols-1 and ord(self.getCell(x,y+1)) == ord(r):
                continue
            return False
        # check for islands using flood fill
        self.fills = [0] * self.num_squares
        for n in range(self.num_squares):
            if self.fills[n] == 0:
                if self.floodFillCount(cells,n) != self.num_symbols:
                    return False
        if self.is_too_perfect_jigsaw_grid(cells):
            return False
        return True

    def pushJQueue(self, n):
        if self.nbrUsed[n] == 0:
            logging.info("! returning extra color: %d" % (n))
        self.nbrUsed[n] -= 1
        self.totUsed -= 1

    def popJQueue(self, n):
        if self.nbrUsed[n] == self.num_symbols:
            logging.info("!! removing zero color: %d" % (n))
            sys.exit()
            return
        self.nbrUsed[n] += 1
        self.totUsed += 1

    def getUnplacedRegion(self):
        if self.totUsed < self.num_squares:
            for i in range(self.num_symbols):
                self.regionCtr = (self.regionCtr + 1) % self.num_symbols
                if self.nbrUsed[self.regionCtr] < self.num_symbols:
                    self.popJQueue(self.regionCtr)
                    return self.regionCtr
            logging.info("! no non-empty regions found")
        return -1
    
    # prefer non-bottleneck neighbors to expand into so we don't split regions into multiple pieces
    def pick_good_neighbor(self, neighbors):
        # Divide neighbors into bottlenecks and non-bottlenecks
        grp_bottlenecks = []
        grp_nonbottlenecks = []

        for idx in neighbors:
            x, y = idx % self.num_symbols, idx // self.num_symbols
            v = self.cells[idx]  # should be '.' (unfilled), but irrelevant for checking neighbors

            # Get values of up/down and left/right neighbors
            up = self.cells[(y-1)*self.num_symbols + x] if y > 0 else None
            down = self.cells[(y+1)*self.num_symbols + x] if y < self.num_symbols-1 else None
            left = self.cells[y*self.num_symbols + (x-1)] if x > 0 else None
            right = self.cells[y*self.num_symbols + (x+1)] if x < self.num_symbols-1 else None

            # Determine if up/down match and left/right don't
            if up is not None and down is not None and up == down and up == v and up != '.' and (
               (left is None or left == '.' or left != up) and (right is None or right == '.' or right != up)
            ):
                grp_bottlenecks.append(idx)
                continue

            # Determine if left/right match and up/down don't
            if left is not None and right is not None and left == right and left == v and left != '.' and (
               (up is None or up == '.' or up != left) and (down is None or down == '.' or down != left)
            ):
                grp_bottlenecks.append(idx)
                continue

            # Else, non-bottleneck
            grp_nonbottlenecks.append(idx)

        # Prefer non-bottlenecks
        if grp_nonbottlenecks:
            return random.choice(grp_nonbottlenecks)
        elif grp_bottlenecks:
            return random.choice(grp_bottlenecks)
        else:
            # fallback, nothing to pick, just pick randomly I guess
            return random.choice(neighbors)

    def growth_fill_pass(self):
        # print("gfp",''.join(self.cells),self.totUsed)
        self.method_type = 0
        if self.totUsed < self.num_squares:
            n = self.getUnplacedRegion()
            if n == -1:
                logging.info("Failed to get unplaced region")
            # print("  ",n)
            if self.nbrUsed[n] == 1: # ? unused
                self.method_type = 1 # random placement
                idx = 0
                while True:
                    idx = random.randrange(self.num_squares)
                    if self.cells[idx] == '.':
                        break
                (cx,cy) = (idx % self.num_symbols, idx // self.num_symbols)
                self.cells[idx] = chr(ord('A')+n)
                if self.cells[idx] == '@':
                    logging.info("@A!!")
                # print("  added",idx)
                if self.symFlags != 0:
                    for i in range(self.num_symbols):
                        if i != n and self.pairedColors[i] == -1:
                            self.pairedColors[n] = i
                            self.pairedColors[i] = n
                            break
                    x2 = (self.num_symbols-1)-cx if (self.symFlags & 0x05) != 0 else cx
                    y2 = (self.num_symbols-1)-cy if (self.symFlags & 0x06) != 0 else cy
                    if x2 != cx or y2 != cy:
                        idx2 = y2*self.num_symbols + x2
                        self.cells[idx2] = chr(ord('A')+self.pairedColors[n])
                        if self.cells[idx2] == '@':
                            logging.info("@B!!")
                        # print("    addeds",idx2)
                        self.popJQueue(self.pairedColors[n])
            else:
                self.method_type = 2 # docking
                # print("docking")
                docks = []
                neighbors = []
                for i in range(self.num_squares):
                    (x,y) = (i % self.num_symbols, i // self.num_symbols)
                    if (x > 0 and self.getCell(x-1,y) == chr(ord('A')+n)) \
                    or (y > 0 and self.getCell(x,y-1) == chr(ord('A')+n)) \
                    or (x < self.num_symbols-1 and self.getCell(x+1,y) == chr(ord('A')+n)) \
                    or (y < self.num_symbols-1 and self.getCell(x,y+1) == chr(ord('A')+n)):
                        if self.cells[i] == '.':
                            docks.append(i)
                        elif not self.isBridge(self.cells, i) and not self.isSelfReflexive(x,y) \
                        and self.nbrUsed[ord(self.cells[i]) - ord("A")] != 1:
                            neighbors.append(i)
                if len(docks) == 0:
                    self.method_type = 3 # no neighbors nor docks
                    if len(neighbors) == 0:
                        self.pushJQueue(n)
                        logging.info("no neighbors nor docks for region" + chr(ord('A')+n) + " " + str(docks)+ " " + str(neighbors))
                        return
                    nidx = self.pick_good_neighbor(neighbors)
                    # nidx = random.choice(neighbors)
                    (ncx,ncy) = (nidx % self.num_symbols, nidx // self.num_symbols)
                    docks.append(nidx)
                    self.pushJQueue(ord(self.cells[nidx]) - ord("A"))
                    self.cells[nidx] = '.'
                    # print("  blanked",nidx)
                    if self.symFlags != 0:
                        x2 = (self.num_symbols-1)-ncx if (self.symFlags & 0x05) != 0 else ncx
                        y2 = (self.num_symbols-1)-ncy if (self.symFlags & 0x06) != 0 else ncy
                        if x2 != ncx or y2 != ncy:
                            nidx2 = y2 * self.num_symbols + x2
                            self.pushJQueue(ord(self.cells[nidx2]) - ord('A'))
                            self.cells[nidx2] = '.'
                            # print("    blankeds",nidx)
                didx = random.choice(docks)
                (dcx,dcy) = (didx % self.num_symbols, didx // self.num_symbols)
                self.cells[didx] = chr(ord('A') + n)
                if self.cells[didx] == '@':
                    logging.info("@D!!")
                # print("  2added",didx)
                if self.symFlags != 0:
                    x2 = (self.num_symbols-1)-dcx if (self.symFlags & 0x05) != 0 else dcx
                    y2 = (self.num_symbols-1)-dcy if (self.symFlags & 0x06) != 0 else dcy
                    if x2 != dcx or y2 != dcy:
                        didx2 = y2 * self.num_symbols + x2
                        self.cells[didx2] = chr(ord('A') + self.pairedColors[n])
                        if self.cells[didx2] == '@':
                            logging.info("@C!!")
                        # print("  2addeds",didx2)
                        self.popJQueue(self.pairedColors[n])

    def growth_fill(self):
        global attempts, layout_draw_counter, layout_draw_dir, debug_draw, sym_buckets
        complete = False
        self.totUsed = 0

        while not complete:
            attempts += 1
            self.init_growth_fill()
            if debug_draw:
                self.draw_layout(os.path.join(layout_draw_dir, f"layout_{layout_draw_counter:03d}.png"),f"init")
                layout_draw_counter += 1
            passes = 0
            while self.totUsed < self.num_squares and passes < 1000:
                self.growth_fill_pass()
                if debug_draw:
                    self.draw_layout(os.path.join(layout_draw_dir, f"layout_{layout_draw_counter:03d}.png"),f"method_type {self.method_type}")
                    layout_draw_counter += 1
                passes += 1
            if self.totUsed == self.num_squares:
                # print("tot_used",self.totUsed)
                if self.is_too_perfect_jigsaw_grid(self.cells):
                    continue
                if not self.is_grid_legal(self.cells):
                    continue
                complete = True
            else:
                continue
        sym_buckets[self.symFlags] += 1
        return self.cells

    # translate cells to sorted order
    def translateSymbols(self):
        cr = "A"
        mapping = [0] * self.num_symbols
        outs = ""
        for n in range(self.num_squares):
            r = self.cells[n]
            if r == '.':
                continue
            if mapping[ord(r)-ord("A")] == 0:
                mapping[ord(r)-ord("A")] = cr
                cr = chr(ord(cr)+1)
            outs += mapping[ord(r)-ord("A")]
        return outs

# it seems likely these grids won't necessarily make a valid puzzle - need to skip bad ones
# as part of puzzle construction (or verify them here)
def jigsaw_maker(num_symbols):
    jm = JigsawMaker(num_symbols)
    jm.growth_fill()
    outs = jm.translateSymbols()
    return outs

from layout_classic import Layout as ClassicLayout
import sys

class Layout(ClassicLayout):
    def __init__(self, num_symbols, ptype, layoutInit = None):
        self.layout = layoutInit
        super().__init__(num_symbols, ptype)

    def setup_blocks(self):
        # jigsaws
        if self.layout is None:
            self.layout = jigsaw_maker(self.num_symbols)
        self.setup_blocks_by_layout(self.layout)
        # for letter in "ABCDEFGHIJKLMNOP"[:self.num_symbols]:
        #     cont = [addr for addr,ch in enumerate(self.layout) if ch == letter]
        #     self.containers.append(tuple(cont))

    def copy(self):
        l2 = Layout(self.num_symbols, self.ptype, self.layout)
        # l2.containers = self.containers.copy()
        return l2

    def get_prefix(self):
        return self.ptype + "\t" + self.layout

    # def draw_layout(self, draw, draw_dimensions):
    #     lm,tm,gw,gh,cw,ch = draw_dimensions['lm'],draw_dimensions['tm'],draw_dimensions['gw'],draw_dimensions['gh'],draw_dimensions['cw'],draw_dimensions['ch']

    #     # for y in range(0,self.num_symbols+1,3):
    #     #     draw.line((lm,tm+y*ch,lm+gw*cw,tm+y*ch),fill='black',width=3)
    #     # for x in range(0,self.num_symbols+1,3):
    #     #     draw.line((lm+x*cw,tm,lm+x*cw,tm+gh*ch),fill='black',width=3)
    #     # draw a 3-width rectangle around the entire puzzle
    #     draw.rectangle((lm,tm,lm+gw*cw,tm+gh*ch),fill=None,outline='black',width=4)
    #     # for each cell, 
    #     #   if the layout letter is different from the following cell, draw a line on the right side of the cell
    #     #   if the layout letter is different from the next-row cell, draw a line on the bottom side of the cell
    #     for y in range(self.num_symbols):
    #         for x in range(self.num_symbols):
    #             cell_addr = y*self.num_symbols + x
    #             cell_letter = self.layout[cell_addr]
    #             if x < self.num_symbols-1 and self.layout[cell_addr+1] != cell_letter:
    #                 draw.line((lm+x*cw+cw,tm+y*ch,lm+x*cw+cw,tm+y*ch+ch),fill='black',width=4)
    #             if y < self.num_symbols-1 and self.layout[cell_addr+self.num_symbols] != cell_letter:
    #                 draw.line((lm+x*cw,tm+y*ch+ch,lm+x*cw+cw,tm+y*ch+ch),fill='black',width=4)

if __name__ == "__main__":
    import random
    import time
    import argparse
    parser = argparse.ArgumentParser(description='Test jigsaw maker')
    parser.add_argument('-n', '--nbr_tests', type=int, default=1000,
                    help='Number of puzzles to test (default: %(default)s)')
    parser.add_argument('-dd', '--debug_draw', action='store_true', default=False,
                    help='Draw debug images')
    parser.add_argument('-ns', '--no_symmetry', action='store_true', default=False,
                    help='Disable symmetry')
    args = parser.parse_args()

    no_symmetry = args.no_symmetry

    if args.debug_draw:
        import os
        os.makedirs(layout_draw_dir, exist_ok=True)
        debug_draw = True
        random.seed(1)
        res = jigsaw_maker(9)
        print(f"Attempts: {attempts} {100*attempts/1:.2f}%")
    else:
        start_time = time.time()
        random.seed(1)
        nbr_tests = args.nbr_tests
        for i in range( nbr_tests):
            # print(jigsaw_maker(9))
            res = jigsaw_maker(9)
        elapsed_time = time.time() - start_time
        print(f"nbr tests: {nbr_tests}")
        print(f"Elapsed time: {elapsed_time:.2f} seconds")
        print(f"Average time per puzzle: {elapsed_time/nbr_tests:.2f} seconds")
        print(f"Layouts per second: {nbr_tests/elapsed_time:.2f}")
        print(f"Attempts: {attempts} {100*attempts/nbr_tests:.2f}% per-puzzle {attempts/nbr_tests:.2f}")
        print(f"Sym buckets: {sym_buckets}")
