# print_puzzles.py
# -*- coding: utf-8 -*-

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import argparse, time
import print_config as cfg
import random
from print_logo import print_logo
from puzzle_record import PuzzleRecord
import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', action='store_true')
parser.add_argument('-d', '--debug', action='store_true')
parser.add_argument('-n', '--nbr_puzzles', type=int)
parser.add_argument('-b', '--book', type=int, default=1)
parser.add_argument('-vol', '--vol', type=int, default=1)
parser.add_argument('-title','--title_override')
parser.add_argument('-subtitle', '--subtitle_override')
parser.add_argument('-year', '--year', type=int, default=datetime.datetime.now().year)
parser.add_argument('ifilename')
parser.add_argument('ofilename')

args = parser.parse_args()

# read the puzzle file
st = time.time()
puzzles = []

line_offset = 1 + (args.book-1)*cfg.puzzles_per_book
if not args.nbr_puzzles:
    args.nbr_puzzles = cfg.puzzles_per_book
page_title = (args.title_override if args.title_override else cfg.page_title)
page_title = page_title.replace("<VOL>", str(args.vol)).replace("<BOOK>", str(args.book))
page_subtitle = (args.subtitle_override if args.subtitle_override else cfg.page_subtitle)
page_subtitle = page_subtitle.replace("<VOL>", str(args.vol)).replace("<BOOK>", str(args.book))

with open(args.ifilename) as f:
    pctr = 0
    for line in f:
        if line[0] == '#' or not line.strip():
            continue
        pctr += 1
        if pctr < line_offset:
           continue
        if args.verbose:
            print("parsing puzzle", line)
        puzrec = PuzzleRecord.parse_puzzle(line)
        puzzles.append(puzrec)
        if args.nbr_puzzles and len(puzzles) == args.nbr_puzzles:
            break

if len(puzzles) == 0:
    print("No puzzles found in %s" % args.ifilename)
    exit(1)

# create the file and start printing it
c = canvas.Canvas(args.ofilename, pagesize=(cfg.page_width, cfg.page_height), pageCompression=1)
# puzzlePrinter = PuzzlePrinterClass(c, cfg, args)
pdfmetrics.registerFont(TTFont('PuzzleTitleFont', cfg.puzzle_title_font))
pdfmetrics.registerFont(TTFont('PuzzleClueFont', cfg.puzzle_clue_font))
pdfmetrics.registerFont(TTFont('PuzzleCopyFont', cfg.puzzle_copy_font))

c.setAuthor(cfg.author)
c.setTitle(cfg.page_title)
c.setSubject(cfg.subject)

def load_lime_pics():
    from glob import glob
    pics = ['./assets/lime_slice_1.png'] # , './assets/lime_slice_2.png', './assets/lime_slice_3.png', './assets/lime_slice_4.png']
    return pics

def load_citrus_pics():
    from glob import glob
    pics = ['./assets/lime_slice_1.png', './assets/orange_slice_1.png', './assets/lemon_slice_1.png'] # 
    return pics


# pics = load_pics()

lime_pics = None
citrus_pics = None
pic_index = 0
fruit_rad = [0.275,0.4,0.325]

def draw_puzzle(canv, prec, pw, ph, opx, opy, show_answer=False):
    global lime_pics, citrus_pics, pic_index
    # if show_answer:
    #     print(f"Drawing answer for {prec['label']} at {opx},{opy}, {pw},{ph}")
    givens = prec.clues_string
    solution = prec.answer_string
    layoutmap = prec.layout.layout
    is_circle9 = False # 'circle9' in prec['ptype']
    is_lime = True # 'lime' in prec['ptype']
    is_citrus = False # 'citrus' in prec['ptype']

    if is_lime and lime_pics is None:
        lime_pics = load_lime_pics() 
    if is_citrus and citrus_pics is None:
        print("Loading citrus pics")
        citrus_pics = load_citrus_pics() 
    puzzle_width = pw
    puzzle_height = ph # will be negative
    gw, gh = 9, 9
    cw, ch = puzzle_width / gw, puzzle_height / gh

    canv.setLineCap(1)  # 1 == round
    canv.setLineJoin(1) # round
    canv.setLineWidth(cw * cfg.thin_line_ratio)
    canv.setStrokeGray(cfg.thin_line_color)

    canv.saveState()
    canv.translate(opx, opy)

    # darken windows
    if 'windows' in prec.puzzle_type:
        canv.saveState()
        canv.setFillGray(cfg.window_color)
        for gy in range(2):
            for gx in range(2):
                canv.rect(cw + cw*4*gx,ch + ch*4*gy,cw*3,ch*3,stroke=0,fill=1)
        canv.restoreState()

    # darken major diagonals
    if 'diag' in prec.puzzle_type:
        canv.saveState()
        # canv.setLineCap(0)  # 1 == round
        line_width = cw * cfg.diagonal_line_ratio
        canv.setLineWidth(line_width)
        canv.setStrokeGray(cfg.diagonal_line_color)
        inset = line_width/2
        canv.line(0+inset,0-inset,gw*cw-inset,gh*ch+inset)
        canv.line(0+inset,gh*ch+inset,gw*cw-inset,0-inset)
        canv.restoreState()

    if 'centerdot' in prec.puzzle_type:
        canv.saveState()
        canv.setFillGray(cfg.center_dot_color)
        for gy in range(3):
            for gx in range(3):
                canv.rect(cw + cw*3*gx,ch + ch*3*gy,cw,ch,stroke=0,fill=1)
        canv.restoreState()


    if 'jig' not in prec.puzzle_type:
        bw, bh = 3,3
        canv.setLineWidth(cw * cfg.thin_line_ratio)
        canv.setStrokeGray(cfg.thin_line_color)
        for y in range(gh):
            if y % bh != 0:
                canv.line(0,ch*y,gw*cw,ch*y)

        for x in range(gw):
            if x % bw != 0:
                canv.line(cw*x,0,cw*x,gh*ch)
        canv.setLineWidth(cw * cfg.thick_line_ratio)
        canv.setStrokeGray(cfg.thick_line_color)
        for y in range(0,gh+1,bw):
            canv.line(0,ch*y,gw*cw,ch*y)

        for x in range(0,gw+1,bh):
            canv.line(cw*x,0,cw*x,gh*ch)
    else:
        canv.setLineWidth(cw * cfg.thin_line_ratio)
        canv.setStrokeGray(cfg.thin_line_color)
        for y in range(gh):
            canv.line(0,ch*y,gw*cw,ch*y)

        for x in range(gw):
            canv.line(cw*x,0,cw*x,gh*ch)
        # draw jigsaw lines
        canv.setLineWidth(cw * cfg.thick_line_ratio)
        canv.setStrokeGray(cfg.thick_line_color)
        if args.verbose:
            print("Drawing Layout",layoutmap,puzzle_width, puzzle_height,cw,ch,gw,gh)
        for y in range(gh):
            for x in range(gw):
                py = ch*y
                px = cw*x
                if y == 0 or layoutmap[(y-1)*gw+x] != layoutmap[y*gw+x]:
                    # top line
                    canv.line(px,py,px+cw,py)
                if y >= gh-1 or layoutmap[(y+1)*gw+x] != layoutmap[y*gw+x]:
                    # bot line
                    canv.line(px,py+ch,px+cw,py+ch)
                if x == 0 or layoutmap[y*gw+(x-1)] != layoutmap[y*gw+x]:
                    # left line
                    canv.line(px,py,px,py+ch)
                if x >= gw-1 or layoutmap[y*gw+(x+1)] != layoutmap[y*gw+x]:
                    # right line
                    canv.line(px+cw,py,px+cw,py+ch)


    font_size = cw*cfg.puzzle_clue_font_size_ratio
    est_font_height = font_size * cfg.est_font_height_ratio
    canv.setFont('PuzzleClueFont',font_size)
    canv.setFillGray(cfg.clue_color)
    canv.saveState()
    # if show_answer and is_circle9:
    #     canv.setLineWidth(cw * cfg.answer_circle_thick_ratio)

    # canv.translate(0,-est_font_height/2)
    # show givens (but skip answers if show_answer is true)
    for y in range(gh):
        for x in range(gw):
            addr = y*gw+x
            if givens[addr] == '.':
                continue
            if show_answer and is_circle9 and solution[addr] == '.':
                continue
            if givens[addr] in '0123456789':
                canv.saveState()
                canv.translate(0,-est_font_height/2)
                canv.drawCentredString(cw*x+cw/2,ch*y+ch/2,givens[addr])
                canv.restoreState()
            elif is_lime and solution[addr] == 'O':
                canv.saveState()
                canv.translate(cw*x+cw/2,ch*y+ch/2)
                canv.rotate(random.randint(1, 180))
                canv.drawImage(lime_pics[pic_index], -cw*.4, -ch*.4, cw*.8, ch*.8, mask='auto')
                pic_index = (pic_index + 1) % len(lime_pics)
                canv.restoreState()
                pic_index = (pic_index + 1) % len(lime_pics)
            elif is_citrus and solution[addr] in 'ABC':
                sol_index = ord(solution[addr]) - ord('A')
                canv.saveState()
                canv.translate(cw*x+cw/2,ch*y+ch/2)
                canv.rotate(random.randint(1, 180))
                frad = fruit_rad[sol_index]
                canv.drawImage(citrus_pics[sol_index], -cw*frad, -ch*frad, cw*2*frad, ch*2*frad, mask='auto')
                canv.restoreState()
    canv.restoreState()

    if show_answer:
        if is_circle9:
            # draw circles
            canv.saveState()
            canv.setLineWidth(cw * cfg.answer_circle_thick_ratio)
            circle_rad = est_font_height*1.4/2
            for y in range(gh):
                for x in range(gw):
                    addr = y*gw+x
                    if givens[addr] == '.':
                        continue
                    if show_answer and solution[addr] == '.':
                        continue
                    canv.circle(cw*x+cw/2,ch*y+ch/2,circle_rad,stroke=1,fill=0)
            canv.restoreState()

            canv.saveState()
            canv.translate(0,-est_font_height/2)
            canv.setFillGray(cfg.cancel_color)
            for y in range(gh):
                for x in range(gw):
                    addr = y*gw+x
                    if givens[addr] == '.':
                        continue
                    if solution[addr] != '.':
                        continue
                    canv.drawCentredString(cw*x+cw/2,ch*y+ch/2,givens[addr])
            canv.restoreState()
        elif is_lime:
            # render circle for each O in solution
            circle_rad = cw * .3
            canv.saveState()
            # canv.translate(0,est_font_height/2)
            canv.setLineWidth(cw * cfg.answer_circle_thick_ratio)
            # set fill color to green     meat_color = (177/255, 201/255, 43/255)  # Meat color (lime green)
            canv.setStrokeColor((88/255, 133/255, 37/255))
            canv.setFillColor((177/255, 201/255, 43/255))
            for y in range(gh):
                for x in range(gw):
                    addr = y*gw+x
                    if solution[addr] != 'O':
                        continue
                    # canv.circle(cw*x+cw/2,ch*y+ch/2,circle_rad,stroke=1,fill=1)
                    canv.saveState()
                    canv.translate(cw*x+cw/2,ch*y+ch/2)
                    canv.rotate(random.randint(1, 180))
                    canv.drawImage(lime_pics[pic_index], -cw*.4, -ch*.4, cw*.8, ch*.8, mask='auto')
                    pic_index = (pic_index + 1) % len(lime_pics)
                    canv.restoreState()
            canv.restoreState()
        elif is_citrus:
            # render circle for each O in solution
            circle_rad = cw * .3
            canv.saveState()
            # canv.translate(0,est_font_height/2)
            canv.setLineWidth(cw * cfg.answer_circle_thick_ratio)
            # set fill color to green     meat_color = (177/255, 201/255, 43/255)  # Meat color (lime green)
            canv.setStrokeColor((88/255, 133/255, 37/255))
            canv.setFillColor((177/255, 201/255, 43/255))
            for y in range(gh):
                for x in range(gw):
                    addr = y*gw+x
                    if solution[addr] in '.0123456789':
                        continue
                    sol_index = ord(solution[addr]) - ord('A')
                    # canv.circle(cw*x+cw/2,ch*y+ch/2,circle_rad,stroke=1,fill=1)
                    canv.saveState()
                    canv.translate(cw*x+cw/2,ch*y+ch/2)
                    canv.rotate(random.randint(1, 180))
                    frad = fruit_rad[sol_index]
                    canv.drawImage(citrus_pics[sol_index], -cw*frad, -ch*frad, cw*2*frad, ch*2*frad, mask='auto')
                    canv.restoreState()
            canv.restoreState()
    canv.restoreState()

c.beginForm("logoForm")
print_logo(c,cfg.page_width,cfg.page_height,390,740)
c.endForm()

lime_pics = load_lime_pics()

for i,prec in enumerate(puzzles):
    # print the puzzle
    puzzle_title = F"#{i+1}"
    # print the title
    c.setFont('PuzzleTitleFont', cfg.puzzle_title_font_size)
    c.setFillGray(cfg.title_color)

    title_prefix = "LIME SUD"
    title_suffix = "KU"
    lime_width = 20
    lime_margin_left = -1
    lime_margin_right = 0

    x_width = pdfmetrics.stringWidth(title_prefix, 'PuzzleTitleFont', cfg.puzzle_title_font_size)

    c.drawString(cfg.left_margin, cfg.page_height - cfg.page_title_y, title_prefix)
    c.drawString(cfg.left_margin + x_width + lime_width + lime_margin_left + lime_margin_right, cfg.page_height - cfg.page_title_y, title_suffix)
    c.drawRightString(cfg.page_width - cfg.right_margin, cfg.page_height - cfg.page_title_y, page_subtitle)

    c.saveState()
    c.translate(cfg.left_margin + x_width + lime_margin_left, cfg.page_height - cfg.page_title_y)
    img = lime_pics[0]
    c.drawImage(img, 0, -lime_width * .5 + lime_width * .32, lime_width, lime_width, mask='auto')
    c.restoreState()


    c.setFillGray(cfg.title_color)
    # c.drawCentredString(cfg.page_width/2, cfg.page_height - cfg.title_height, title)
    c.drawString((cfg.page_width - cfg.puzzle_width)/2, cfg.page_height - cfg.puzzle_title_y, puzzle_title)

    c.doForm("logoForm")
    # print_logo(c,cfg.page_width,cfg.page_height,390,740)

    # instructions
    instructions = cfg.instructions[prec.puzzle_type]
    c.setFont('PuzzleCopyFont', cfg.puzzle_instructions_size)
    for y,iline in enumerate(instructions):
        c.drawString(cfg.left_margin, cfg.page_height - (cfg.instructions_top + y*cfg.instructions_lheight), iline)

    c.setFont('PuzzleCopyFont', cfg.puzzle_legalese_size)
    c.drawRightString(cfg.page_width/2 + cfg.puzzle_width/2,  cfg.page_height - (cfg.puzzle_top+cfg.puzzle_height+12), cfg.copyright_string.replace("<YEAR>", str(args.year)))
    # if 'lime' not in prec.puzzle_type:
    #     c.drawString(cfg.left_margin,  cfg.bottom_margin, cfg.attribution_string)
    # else:
    #     c.drawString(cfg.left_margin,  cfg.bottom_margin, cfg.attribution_string_lime)

    draw_puzzle(c, prec, cfg.puzzle_width, -cfg.puzzle_height, (cfg.page_width - cfg.puzzle_width)/2, cfg.page_height - cfg.puzzle_top)
    c.showPage()

# print answers here...
anbr = 0
c.setFont('PuzzleTitleFont', cfg.puzzle_atitle_font_size)
c.setFillGray(cfg.title_color)
for gy in range(cfg.answers_down):
    for gx in range(cfg.answers_across):
        prec = puzzles[anbr]
        anbr += 1
        atitle = F"#{anbr}"
        px = cfg.answers_left+gx*(cfg.answer_width+cfg.answer_gapx)
        py = cfg.answers_top+gy*(cfg.answer_height+cfg.answer_gapy)
        # print("!",px,py)
        c.drawString(px, cfg.page_height - (py-4), atitle)
        draw_puzzle(c, prec, cfg.answer_width, -cfg.answer_height, px, cfg.page_height-py, show_answer=True)
c.doForm("logoForm")
# print_logo(c,cfg.page_width,cfg.page_height,390,740)
c.showPage()

c.save()
print("Wrote %d puzzles to %s" % (len(puzzles), args.ofilename))
