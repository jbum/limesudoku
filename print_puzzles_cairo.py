# print_puzzles_cairo.py
# -*- coding: utf-8 -*-

import argparse
import math
import random
import time
import cairo
from lxml import etree as ET
import re
import os
from puzzle_record import PuzzleRecord
import print_config as cfg
import datetime

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-n', '--nbr_puzzles', type=int)
    parser.add_argument('-b', '--book', type=int, default=1)
    parser.add_argument('-vol', '--vol', type=int, default=1)
    parser.add_argument('-title', '--title_override')
    parser.add_argument('-subtitle', '--subtitle_override')
    parser.add_argument('-year', '--year', type=int, default=datetime.datetime.now().year)
    parser.add_argument('ifilename')
    parser.add_argument('ofilename')
    return parser.parse_args()


def read_puzzles(args):
    st = time.time()
    puzzles = []

    line_offset = 1 + (args.book - 1) * cfg.puzzles_per_book
    if not args.nbr_puzzles:
        args.nbr_puzzles = cfg.puzzles_per_book
    page_title = (args.title_override if args.title_override else cfg.page_title)
    page_title = page_title.replace("<VOL>", str(args.vol)).replace("<BOOK>", str(args.book))
    page_subtitle = (args.subtitle_override if args.subtitle_override else cfg.page_subtitle)
    page_subtitle = page_subtitle.replace("<VOL>", str(args.vol)).replace("<BOOK>", str(args.book))

    with open(args.ifilename) as f:
        pctr = 0
        for line in f:
            if not line:
                continue
            if line[0] == '#':
                continue
            pctr += 1
            if pctr < line_offset:
                continue
            # !! REWRITE USING puzzle_class
            puzrec = PuzzleRecord.parse_puzzle(line)
            puzzles.append(puzrec)
            if args.nbr_puzzles and len(puzzles) == args.nbr_puzzles:
                break

    if len(puzzles) == 0:
        print(f"No puzzles found in {args.ifilename}")
        raise SystemExit(1)

    return puzzles, page_title, page_subtitle


# -------- Cairo helpers --------

def new_pdf_surface(filename, width, height):
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
    surface = cairo.PDFSurface(filename, width, height)
    ctx = cairo.Context(surface)
    # Flip Y axis so that coordinates match reportlab's bottom-left origin logic
    ctx.translate(0, height)
    ctx.scale(1, -1)
    # Use round caps/joins similar to reportlab
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    return surface, ctx


def set_gray_source(ctx, g):
    ctx.set_source_rgb(g, g, g)


def draw_line(ctx, x1, y1, x2, y2):
    ctx.new_path()
    ctx.move_to(x1, y1)
    ctx.line_to(x2, y2)
    ctx.stroke()


def draw_rect(ctx, x, y, w, h, stroke=0, fill=1):
    ctx.new_path()
    ctx.rectangle(x, y, w, h)
    if fill and stroke:
        ctx.fill_preserve()
        ctx.stroke()
    elif fill:
        ctx.fill()
    elif stroke:
        ctx.stroke()


def draw_circle(ctx, cx, cy, r, stroke=1, fill=0):
    ctx.new_path()
    ctx.arc(cx, cy, r, 0, 2 * math.pi)
    if fill and stroke:
        ctx.fill_preserve()
        ctx.stroke()
    elif fill:
        ctx.fill()
    elif stroke:
        ctx.stroke()


# Text helpers using Cairo toy text API

FONT_TITLE = ('Helvetica', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
FONT_PUZZLENUMBER = ('Helvetica', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
FONT_CLUE = ('Helvetica', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
FONT_COPY = ('Helvetica', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)


def select_font(ctx, family_slant_weight, size):
    family, slant, weight = family_slant_weight
    ctx.select_font_face(family, slant, weight)
    ctx.set_font_size(size)


def text_width(ctx, text):
    te = ctx.text_extents(text)
    return te.width


def show_text_upright(ctx, x, y, text):
    ctx.save()
    # Counteract the global Y-flip for text so glyphs are upright
    ctx.scale(1, -1)
    ctx.move_to(x, -y)
    ctx.show_text(text)
    ctx.restore()

def draw_left_text(ctx, x_left, y_baseline, text):
    te = ctx.text_extents(text)
    show_text_upright(ctx, x_left, y_baseline, text)

def draw_right_text(ctx, x_right, y_baseline, text):
    te = ctx.text_extents(text)
    show_text_upright(ctx, x_right - te.x_advance, y_baseline, text)


def draw_centered_text(ctx, x_center, y_baseline, text):
    te = ctx.text_extents(text)
    show_text_upright(ctx, x_center - te.x_advance / 2.0, y_baseline, text)


# Image helpers

def load_png(path):
    return cairo.ImageSurface.create_from_png(path)


def draw_image(ctx, surf, x, y, w, h):
    iw = surf.get_width()
    ih = surf.get_height()
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(w / iw, h / ih)
    ctx.set_source_surface(surf, 0, 0)
    ctx.paint()
    ctx.restore()


# Logo rendering (SVG path to Cairo path), adapted from print_logo.py

def draw_logo(ctx, pw, ph, ox, oy, justify='left', filename='assets/krazydad_logo_new_slogan.svg'):
    svg = ET.parse(filename)
    oy = oy - 28
    if justify == 'right':
        ox = ox - 150
    elif justify == 'center':
        ox = ox - 150 / 2

    # Fill black
    set_gray_source(ctx, 0)

    for gelem in svg.getroot().iterdescendants(tag='{http://www.w3.org/2000/svg}g'):
        for pelem in gelem.iterdescendants(tag='{http://www.w3.org/2000/svg}path'):
            d = pelem.attrib.get('d', '')
            if not d:
                continue
            clist = re.split('(:?[A-Za-z])', d)[1:]
            x1 = y1 = x2 = y2 = 0.0
            px = ox
            py = oy
            ctx.new_path()
            while len(clist) > 1:
                cmd, pts = clist[0:2]
                clist = clist[2:]
                pts = re.sub('-', ',-', pts)
                pts = re.sub('^,', '', pts)
                if cmd.upper() in 'MCSHVL':
                    plist = [float(x) for x in pts.split(',') if x != '']
                    if cmd == 'M':
                        px, py = plist[0] + ox, plist[1] + oy
                        ctx.move_to(px, ph - py)
                    elif cmd == 'm':
                        px, py = plist[0] + px, plist[1] + py
                        ctx.move_to(px, ph - py)
                    elif cmd == 'L':
                        px, py = plist[0] + ox, plist[1] + oy
                        ctx.line_to(px, ph - py)
                    elif cmd == 'l':
                        px, py = plist[0] + px, plist[1] + py
                        ctx.line_to(px, ph - py)
                    elif cmd == 'H':
                        px = plist[0] + ox
                        ctx.line_to(px, ph - py)
                    elif cmd == 'h':
                        px = plist[0] + px
                        ctx.line_to(px, ph - py)
                    elif cmd == 'V':
                        py = plist[0] + oy
                        ctx.line_to(px, ph - py)
                    elif cmd == 'v':
                        py = plist[0] + py
                        ctx.line_to(px, ph - py)
                    elif cmd == 'C':
                        x1, y1, x2, y2, px, py = (
                            plist[0] + ox, plist[1] + oy,
                            plist[2] + ox, plist[3] + oy,
                            plist[4] + ox, plist[5] + oy,
                        )
                        ctx.curve_to(x1, ph - y1, x2, ph - y2, px, ph - py)
                    elif cmd == 'c':
                        x1, y1, x2, y2, px, py = (
                            plist[0] + px, plist[1] + py,
                            plist[2] + px, plist[3] + py,
                            plist[4] + px, plist[5] + py,
                        )
                        ctx.curve_to(x1, ph - y1, x2, ph - y2, px, ph - py)
                    elif cmd == 'S':
                        x1, y1, x2, y2, px, py = (
                            px - (x2 - px), py - (y2 - py),
                            plist[0] + ox, plist[1] + oy,
                            plist[2] + ox, plist[3] + oy,
                        )
                        ctx.curve_to(x1, ph - y1, x2, ph - y2, px, ph - py)
                    elif cmd == 's':
                        x1, y1, x2, y2, px, py = (
                            px - (x2 - px), py - (y2 - py),
                            plist[0] + px, plist[1] + py,
                            plist[2] + px, plist[3] + py,
                        )
                        ctx.curve_to(x1, ph - y1, x2, ph - y2, px, ph - py)
                elif cmd == 'z':
                    ctx.close_path()
            ctx.fill()


# Assets loading

def load_lime_pics():
    pics = ['./assets/lime_slice_1.png']
    return [load_png(p) for p in pics]


def load_citrus_pics():
    pics = ['./assets/lime_slice_1.png', './assets/orange_slice_1.png', './assets/lemon_slice_1.png']
    return [load_png(p) for p in pics]


# Cached recording surface for the logo
logo_recording_surface = None

def ensure_logo_recording_surface():
    global logo_recording_surface
    if logo_recording_surface is not None:
        return logo_recording_surface
    # Record at page dimensions; the recording includes absolute placement for the logo
    extents = (0, 0, cfg.page_width, cfg.page_height)
    logo_recording_surface = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, extents)
    rctx = cairo.Context(logo_recording_surface)
    # The recording context is not y-flipped; draw_logo accounts for top-origin using ph - py
    draw_logo(rctx, cfg.page_width, cfg.page_height, 390, 740)
    return logo_recording_surface


def paint_logo(ctx):
    rsurf = ensure_logo_recording_surface()
    ctx.save()
    ctx.set_source_surface(rsurf, 0, 0)
    ctx.paint()
    ctx.restore()


# -------- Main drawing routine --------

lime_pics = None
citrus_pics = None
pic_index = 0
fruit_rad = [0.275, 0.4, 0.325]


def draw_puzzle(ctx, prec, pw, ph, opx, opy, show_answer=False, verbose=False):
    global lime_pics, citrus_pics, pic_index

    givens = prec.clues_string
    solution = prec.answer_string
    layoutmap = prec.layout.layout
    is_circle9 = False # 'circle9' in prec['ptype']
    is_lime = True # 'lime' in prec['ptype']
    is_citrus = False # 'citrus' in prec['ptype']

    if is_lime and lime_pics is None:
        lime_pics = load_lime_pics()
    if is_citrus and citrus_pics is None:
        citrus_pics = load_citrus_pics()

    puzzle_width = pw
    puzzle_height = ph  # may be negative, same as reportlab version
    gw, gh = 9, 9
    cw, ch = puzzle_width / gw, puzzle_height / gh

    # Preserve caller graphics state before any drawing state changes
    ctx.save()
    ctx.translate(opx, opy)

    # Line styles
    ctx.set_line_width(abs(cw) * cfg.thin_line_ratio)
    set_gray_source(ctx, cfg.thin_line_color)

    # darken windows
    if 'windows' in prec.puzzle_type:
        ctx.save()
        set_gray_source(ctx, cfg.window_color)
        for gy in range(2):
            for gx in range(2):
                draw_rect(ctx, cw + cw * 4 * gx, ch + ch * 4 * gy, cw * 3, ch * 3, stroke=0, fill=1)
        ctx.restore()

    # darken major diagonals
    if 'diag' in prec.puzzle_type:
        ctx.save()
        line_width = abs(cw) * cfg.diagonal_line_ratio
        ctx.set_line_width(line_width)
        set_gray_source(ctx, cfg.diagonal_line_color)
        inset = line_width / 2
        draw_line(ctx, 0 + inset, 0 - inset, gw * cw - inset, gh * ch + inset)
        draw_line(ctx, 0 + inset, gh * ch + inset, gw * cw - inset, 0 - inset)
        ctx.restore()

    if 'centerdot' in prec.puzzle_type:
        ctx.save()
        set_gray_source(ctx, cfg.center_dot_color)
        for gy in range(3):
            for gx in range(3):
                draw_rect(ctx, cw + cw * 3 * gx, ch + ch * 3 * gy, cw, ch, stroke=0, fill=1)
        ctx.restore()

    # grid
    if 'jig' not in prec.puzzle_type:
        bw, bh = 3, 3
        ctx.set_line_width(abs(cw) * cfg.thin_line_ratio)
        set_gray_source(ctx, cfg.thin_line_color)
        for y in range(gh):
            if y % bh != 0:
                draw_line(ctx, 0, ch * y, gw * cw, ch * y)
        for x in range(gw):
            if x % bw != 0:
                draw_line(ctx, cw * x, 0, cw * x, gh * ch)
        ctx.set_line_width(abs(cw) * cfg.thick_line_ratio)
        set_gray_source(ctx, cfg.thick_line_color)
        for y in range(0, gh + 1, bw):
            draw_line(ctx, 0, ch * y, gw * cw, ch * y)
        for x in range(0, gw + 1, bh):
            draw_line(ctx, cw * x, 0, cw * x, gh * ch)
    else:
        ctx.set_line_width(abs(cw) * cfg.thin_line_ratio)
        set_gray_source(ctx, cfg.thin_line_color)
        for y in range(gh):
            draw_line(ctx, 0, ch * y, gw * cw, ch * y)
        for x in range(gw):
            draw_line(ctx, cw * x, 0, cw * x, gh * ch)
        # draw jigsaw lines
        ctx.set_line_width(abs(cw) * cfg.thick_line_ratio)
        set_gray_source(ctx, cfg.thick_line_color)
        if verbose:
            print("Drawing Layout", layoutmap, puzzle_width, puzzle_height, cw, ch, gw, gh)
        for y in range(gh):
            for x in range(gw):
                py = ch * y
                px = cw * x
                if y == 0 or layoutmap[(y - 1) * gw + x] != layoutmap[y * gw + x]:
                    draw_line(ctx, px, py, px + cw, py)
                if y >= gh - 1 or layoutmap[(y + 1) * gw + x] != layoutmap[y * gw + x]:
                    draw_line(ctx, px, py + ch, px + cw, py + ch)
                if x == 0 or layoutmap[y * gw + (x - 1)] != layoutmap[y * gw + x]:
                    draw_line(ctx, px, py, px, py + ch)
                if x >= gw - 1 or layoutmap[y * gw + (x + 1)] != layoutmap[y * gw + x]:
                    draw_line(ctx, px + cw, py, px + cw, py + ch)

    # numbers and images
    font_size = abs(cw) * cfg.puzzle_clue_font_size_ratio
    est_font_height = font_size * cfg.est_font_height_ratio
    select_font(ctx, FONT_CLUE, font_size)
    set_gray_source(ctx, cfg.clue_color)

    ctx.save()
    for y in range(gh):
        for x in range(gw):
            addr = y * gw + x
            if givens[addr] == '.':
                continue
            if show_answer and is_circle9 and solution[addr] == '.':
                continue
            if givens[addr] in '0123456789':
                ctx.save()
                # vertical centering tweak
                show_text_upright(ctx, cw * x + cw / 2 - text_width(ctx, givens[addr]) / 2.0,
                                  ch * y + ch / 2 - est_font_height / 2,
                                  givens[addr])
                ctx.restore()
            elif is_lime and solution[addr] == 'O':
                ctx.save()
                ctx.translate(cw * x + cw / 2, ch * y + ch / 2)
                ctx.rotate(math.radians(random.randint(1, 180)))
                img = lime_pics[pic_index]
                draw_image(ctx, img, -cw * .4, -ch * .4, cw * .8, ch * .8)
                pic_index = (pic_index + 1) % len(lime_pics)
                ctx.restore()
                pic_index = (pic_index + 1) % len(lime_pics)
            elif is_citrus and solution[addr] in 'ABC':
                sol_index = ord(solution[addr]) - ord('A')
                ctx.save()
                ctx.translate(cw * x + cw / 2, ch * y + ch / 2)
                ctx.rotate(math.radians(random.randint(1, 180)))
                frad = fruit_rad[sol_index]
                img = citrus_pics[sol_index]
                draw_image(ctx, img, -cw * frad, -ch * frad, cw * 2 * frad, ch * 2 * frad)
                ctx.restore()
    ctx.restore()

    # answers layer
    if show_answer:
        if is_circle9:
            ctx.save()
            ctx.set_line_width(abs(cw) * cfg.answer_circle_thick_ratio)
            circle_rad = est_font_height * 1.4 / 2
            for y in range(gh):
                for x in range(gw):
                    addr = y * gw + x
                    if givens[addr] == '.':
                        continue
                    if show_answer and solution[addr] == '.':
                        continue
                    draw_circle(ctx, cw * x + cw / 2, ch * y + ch / 2, circle_rad, stroke=1, fill=0)
            ctx.restore()

            ctx.save()
            set_gray_source(ctx, cfg.cancel_color)
            for y in range(gh):
                for x in range(gw):
                    addr = y * gw + x
                    if givens[addr] == '.':
                        continue
                    if solution[addr] != '.':
                        continue
                    show_text_upright(ctx, cw * x + cw / 2 - text_width(ctx, givens[addr]) / 2.0,
                                      ch * y + ch / 2 - est_font_height / 2,
                                      givens[addr])
            ctx.restore()
        elif is_lime:
            circle_rad = abs(cw) * .3
            ctx.save()
            ctx.set_line_width(abs(cw) * cfg.answer_circle_thick_ratio)
            # stroke/fill colors (not used for images, but keep parity)
            for y in range(gh):
                for x in range(gw):
                    addr = y * gw + x
                    if solution[addr] != 'O':
                        continue
                    ctx.save()
                    ctx.translate(cw * x + cw / 2, ch * y + ch / 2)
                    ctx.rotate(math.radians(random.randint(1, 180)))
                    img = lime_pics[pic_index]
                    draw_image(ctx, img, -cw * .4, -ch * .4, cw * .8, ch * .8)
                    pic_index = (pic_index + 1) % len(lime_pics)
                    ctx.restore()
            ctx.restore()
        elif is_citrus:
            ctx.save()
            ctx.set_line_width(abs(cw) * cfg.answer_circle_thick_ratio)
            for y in range(gh):
                for x in range(gw):
                    addr = y * gw + x
                    if solution[addr] in '.0123456789':
                        continue
                    sol_index = ord(solution[addr]) - ord('A')
                    ctx.save()
                    ctx.translate(cw * x + cw / 2, ch * y + ch / 2)
                    ctx.rotate(math.radians(random.randint(1, 180)))
                    frad = fruit_rad[sol_index]
                    img = citrus_pics[sol_index]
                    draw_image(ctx, img, -cw * frad, -ch * frad, cw * 2 * frad, ch * 2 * frad)
                    ctx.restore()
            ctx.restore()

    ctx.restore()


def main():
    global lime_pics
    args = parse_args()

    puzzles, page_title, page_subtitle = read_puzzles(args)

    surface, ctx = new_pdf_surface(args.ofilename, cfg.page_width, cfg.page_height)

    # Build logo recording surface once
    ensure_logo_recording_surface()

    lime_pics = load_lime_pics()

    for i, prec in enumerate(puzzles):
        # page title (top-right)
        select_font(ctx, FONT_TITLE, cfg.puzzle_title_font_size)
        set_gray_source(ctx, cfg.title_color)
        lime_width = 24
        lime_margin = 2
        te = ctx.text_extents(page_title)
        draw_left_text(ctx, cfg.left_margin + lime_width + lime_margin, cfg.page_height - cfg.page_title_y, page_title)
        draw_right_text(ctx, cfg.page_width - cfg.right_margin, cfg.page_height - cfg.page_title_y, page_subtitle)

        ctx.save()
        ctx.translate(cfg.left_margin, cfg.page_height - cfg.page_title_y)
        img = lime_pics[0]
        draw_image(ctx, img, 0, -lime_width * .5 + lime_width*.25, lime_width, lime_width)
        ctx.restore()
        ctx.save()
        ctx.translate(cfg.left_margin + te.x_advance + lime_width + lime_margin*2, cfg.page_height - cfg.page_title_y)
        img = lime_pics[0]
        draw_image(ctx, img, 0, -lime_width * .5 + lime_width*.25, lime_width, lime_width)
        ctx.restore()



        # puzzle counter at top-left of puzzle area
        select_font(ctx, FONT_PUZZLENUMBER, cfg.puzzle_atitle_font_size)
        title = f"#{i+1}"
        set_gray_source(ctx, cfg.title_color)
        show_text_upright(ctx, (cfg.page_width - cfg.puzzle_width) / 2, cfg.page_height - cfg.puzzle_title_y, title)

        # logo via recording surface (reused XObject)
        paint_logo(ctx)

        # instructions
        if prec.puzzle_type not in cfg.instructions:
            print(f"Warning: {prec.puzzle_type} not in instructions")
            continue
        instructions = cfg.instructions[prec.puzzle_type]
        select_font(ctx, FONT_COPY, cfg.puzzle_instructions_size)
        for y, iline in enumerate(instructions):
            draw_left_text(ctx, cfg.left_margin, cfg.page_height - (cfg.instructions_top + y * cfg.instructions_lheight), iline)

        # legalese
        select_font(ctx, FONT_COPY, cfg.puzzle_legalese_size)
        draw_right_text(ctx, cfg.page_width / 2 + cfg.puzzle_width / 2, cfg.page_height - (cfg.puzzle_top + cfg.puzzle_height + 12), cfg.copyright_string.replace("<YEAR>", str(args.year)))
        # if 'lime' not in prec['ptype']:
        #     show_text_upright(ctx, cfg.left_margin, cfg.bottom_margin, cfg.attribution_string)
        # else:
        #     show_text_upright(ctx, cfg.left_margin, cfg.bottom_margin, cfg.attribution_string_lime)

        # puzzle grid
        draw_puzzle(ctx, prec, cfg.puzzle_width, -cfg.puzzle_height, (cfg.page_width - cfg.puzzle_width) / 2, cfg.page_height - cfg.puzzle_top, show_answer=False, verbose=args.verbose)

        # end page
        ctx.show_page()

    # Answers page(s)
    select_font(ctx, FONT_PUZZLENUMBER, cfg.puzzle_atitle_font_size)

    anbr = 0
    for gy in range(cfg.answers_down):
        for gx in range(cfg.answers_across):
            prec = puzzles[anbr]
            anbr += 1
            atitle = f"#{anbr}"
            px = cfg.answers_left + gx * (cfg.answer_width + cfg.answer_gapx)
            py = cfg.answers_top + gy * (cfg.answer_height + cfg.answer_gapy)
            # Ensure title color is black each time
            set_gray_source(ctx, cfg.title_color)
            show_text_upright(ctx, px, cfg.page_height - (py - 4), atitle)
            draw_puzzle(ctx, prec, cfg.answer_width, -cfg.answer_height, px, cfg.page_height - py, show_answer=True, verbose=False)

    # logo again
    paint_logo(ctx)

    ctx.show_page()

    surface.finish()
    print("Wrote %d puzzles to %s" % (len(puzzles), args.ofilename))


if __name__ == '__main__':
    main() 