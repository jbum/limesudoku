#!/usr/bin/env pypy3
"""
lime_steps.py - step-by-step solutions for the krazydad.com Lime Sudoku pages.

Runs the production-rule solver (solve_PR.py) with its step log on, groups the logged
deductions into steps (one step = one rule firing for one clue / container / group),
writes a caption for each from the rule's provenance, and prints JSON in the shape the
website's step overlay consumes (see STEPS.md, and krazydad/limesudoku/steps/README.md).

    pypy3 lime_steps.py --type lime --clues '....2..1....' [--answer ...] [--id KD_lime-easy_V1-B1-P1]
    pypy3 lime_steps.py --type lime-jigsaw --layout AAAB... --clues ...
    pypy3 lime_steps.py --file puzzledata/lime-hard-V1.tsv --index 7          # from a puzzle file
    pypy3 lime_steps.py --file puzzledata/lime-hard-V1.tsv --index 7 --text   # captions only, for review

Cells are named A1..I9 (column letter, row number), as on the Star Battle steps page.
"""
import sys, json, argparse
from puzzle_record import PuzzleRecord
from layout_classic import Layout
from layout_jiggy9 import Layout as JiggyLayout
import solve_PR

VERSION = 1.0
NUM = ['no','one','two','three','four','five','six','seven','eight','nine']
CLASSIC_LAYOUT = 'AAABBBCCCAAABBBCCCAAABBBCCCDDDEEEFFFDDDEEEFFFDDDEEEFFFGGGHHHIIIGGGHHHIIIGGGHHHIII'
WINDOW_LAYOUT = 'ABBBACCCADEEEDFFFDDEEEDFFFDDEEEDFFFDABBBACCCAGHHHGIIIGGHHHGIIIGGHHHGIIIGABBBACCCA'

def A(c):
    """(x,y) -> 'A1'"""
    return chr(65 + c[0]) + str(c[1] + 1)
def AL(cells):
    return ','.join(A(c) for c in cells)
def num(n):
    return NUM[n] if 0 <= n < len(NUM) else str(n)
def limes(n):
    return '%s %s' % (num(n), 'lime' if n == 1 else 'limes')
def plural(n, s, p=None):
    return s if n == 1 else (p if p else s + 's')
def cap(s):
    return s[0].upper() + s[1:] if s else s
def join_and(items):
    items = list(items)
    if len(items) <= 1: return ''.join(items)
    return ', '.join(items[:-1]) + ' and ' + items[-1]

# ---------------------------------------------------------------------------------------
# naming containers and clues
# ---------------------------------------------------------------------------------------
BLOCK_NAMES = ['the top-left block', 'the top block', 'the top-right block',
               'the left block', 'the center block', 'the right block',
               'the bottom-left block', 'the bottom block', 'the bottom-right block']
WINDOW_NAMES = {'E': 'the upper-left window', 'F': 'the upper-right window',
                'H': 'the lower-left window', 'I': 'the lower-right window',
                'A': 'the nine squares where rows 1, 5 and 9 meet columns 1, 5 and 9',
                'B': 'the squares of rows 1, 5 and 9 that lie in columns 2 to 4',
                'C': 'the squares of rows 1, 5 and 9 that lie in columns 6 to 8',
                'D': 'the squares of columns 1, 5 and 9 that lie in rows 2 to 4',
                'G': 'the squares of columns 1, 5 and 9 that lie in rows 6 to 8'}
OUTLINE_COLORS = ['pink', 'cyan', 'yellow', 'blue', 'red']
RING_COLORS = ['blue', 'red', 'green', 'orange']

class Naming:
    """Names containers and clues for one caption and collects what to highlight."""
    def __init__(self, board, ptype):
        self.board = board
        self.ptype = ptype
        self.jigsaw = 'jig' in ptype
        self.rows, self.cols, self.outlines, self.rings = [], [], [], []
        self.green, self.orange, self.gray = [], [], []
    def add(self, which, cells):
        lst = getattr(self, which)
        for c in cells:
            a = A(c) if isinstance(c, tuple) else c
            if a not in lst: lst.append(a)
    def cont(self, ci, capital=False):
        b = self.board
        if ci < 9:
            if ci + 1 not in self.rows: self.rows.append(ci + 1)
            s = 'row %d' % (ci + 1)
        elif ci < 18:
            if ci - 8 not in self.cols: self.cols.append(ci - 8)
            s = 'column %d' % (ci - 8)
        elif ci < 27:
            cells = b.containers[ci]
            key = AL(cells)
            if key not in self.outlines: self.outlines.append(key)
            if self.jigsaw:
                s = '\x01%s\x01' % key   # 'the outlined shape', resolved when all outlines are known
            else:
                s = BLOCK_NAMES[ci - 18]
        else:
            cells = b.containers[ci]
            if 'windows' in self.ptype:
                letter = WINDOW_LAYOUT[cells[0][1]*9 + cells[0][0]]
                s = WINDOW_NAMES.get(letter, 'the shaded window group')
            elif 'diag' in self.ptype:
                s = 'the diagonal from the top-left corner' if cells[0] == (0, 0) else 'the diagonal from the top-right corner'
            elif 'centerdot' in self.ptype:
                s = 'the nine center squares'
            else:
                s = 'the extra region'
        return cap(s) if capital else s
    def clue(self, c, value, capital=False):
        a = A(c)
        if a not in self.rings: self.rings.append(a)
        s = '\x02%s\x02%d' % (a, value)   # 'the circled 3' / 'the blue-circled 3', resolved at the end
        return cap(s) if capital else s
    def finish(self, txt):
        import re
        outlines = self.outlines
        def oname(m):
            if len(outlines) == 1: s = 'the outlined shape'
            else: s = 'the %s-outlined shape' % OUTLINE_COLORS[outlines.index(m.group(1)) % len(OUTLINE_COLORS)]
            return s
        txt = re.sub(r'\x01([A-I0-9,]+)\x01', oname, txt)
        rings = self.rings
        def rname(m):
            a, v = m.group(1), m.group(2)
            if len(rings) == 1: s = 'the circled %s' % v
            else: s = 'the %s-circled %s' % (RING_COLORS[rings.index(a) % len(RING_COLORS)], v)
            return s
        txt = re.sub(r'\x02([A-I][1-9])\x02(\d)', rname, txt)
        # a token that was capitalized by cap() starts with \x01 or \x02, so fix sentence starts
        txt = re.sub(r'(^|\. )the ', lambda m: m.group(1) + 'The ', txt)
        return txt
    def out(self, exclude=()):
        d = {}
        green = [c for c in self.green if c not in exclude]
        if green: d['his'] = ','.join(green)
        orange = [c for c in self.orange if c not in green and c not in exclude]
        if orange: d['hi6s'] = ','.join(orange)
        gray = [c for c in self.gray if c not in green and c not in orange and c not in exclude]
        if gray: d['hi8s'] = ','.join(gray)
        if self.rings: d['hic'] = ','.join(self.rings)
        hl = {}
        if self.rows: hl['rows'] = self.rows
        if self.cols: hl['cols'] = self.cols
        if self.outlines: hl['outlines'] = self.outlines
        if hl: d['rhi'] = hl
        return d

# ---------------------------------------------------------------------------------------
# captions
# ---------------------------------------------------------------------------------------
def need_word(n):
    return 'one more lime' if n == 1 else '%s more limes' % num(n)

def caption_cont_full(p, N, step):
    c = N.cont(p['cont'], True)
    return '%s already has its three limes, so its other open %s (yellow) must be empty.' % (c, plural(len(step['cells']), 'square'))

def caption_cont_empties(p, N, step):
    c = N.cont(p['cont'], True); n = len(step['cells'])
    return '%s has only %s open %s left (yellow) for its remaining %s, so %s.' % (
        c, num(n), plural(n, 'square'), limes(n), 'it must be a lime' if n == 1 else 'they must all be limes')

def caption_clue_full(p, N, step):
    c = N.clue(p['clue'], p['value'], True)
    return '%s already touches %s, so its other open %s (yellow) must be empty.' % (
        c, limes(p['value']), plural(len(step['cells']), 'neighbor'))

def caption_clue_empties(p, N, step):
    c = N.clue(p['clue'], p['value'], True); n = len(step['cells']); have = len(p['mines'])
    if have == 0:
        return '%s has exactly %s open %s left (yellow) for its %s, so %s.' % (
            c, num(n), plural(n, 'neighbor'), limes(p['value']), 'it must be a lime' if n == 1 else 'they must all be limes')
    return '%s still needs %s and has exactly %s open %s left (yellow), so %s.' % (
        c, need_word(p['value'] - have), num(n), plural(n, 'neighbor'), 'it must be a lime' if n == 1 else 'they must all be limes')

def caption_greedy(p, N, step):
    c = N.clue(p['clue'], p['value']); cont = N.cont(p['cont'])
    N.add('green', p['nbrs'])
    return ('%s still needs three limes, and all of its open neighbors (green) lie in %s. Those three limes are all the limes '
            '%s gets, so its other open %s (yellow) must be empty.' % (cap(c), cont, cont, plural(len(step['cells']), 'square')))

def caption_greedy_general(p, N, step):
    c = N.clue(p['clue'], p['value']); cr = N.cont(p['cont_rest'])
    nf = len(p['nbrs_force'])
    N.add('green', p['nbrs_rest'])
    return ('%s needs %s. Only %s of its open neighbors %s outside %s, so at least three of its limes land inside that region (green), '
            'which is all the limes it gets. So the %s outside %s must %s, and the other open squares of %s must be empty (all yellow).' % (
            cap(c), limes(p['value']), num(nf), plural(nf, 'lies', 'lie'), cr,
            plural(nf, 'neighbor'), cr, 'be a lime' if nf == 1 else 'be limes', cr))

def caption_pushy(p, N, step):
    c = N.clue(p['clue'], p['value']); cont = N.cont(p['cont'])
    ext = p['external']; nin = len(p['nbrs_in']); n_ext_mines = len(p['ext_mines']); v = p['value']
    N.add('orange', p['nbrs_in'])
    mines_txt = ('%s already has %s, and ' % (cap(cont), limes(n_ext_mines))) if n_ext_mines else ''
    txt = ('%s%s needs three limes in all. %s can put at most %s of them among its neighbors inside %s (orange), which leaves '
           'exactly %s for the %s open %s of %s away from the clue (yellow), so %s.' % (
           mines_txt, cap(cont) if not n_ext_mines else 'it', cap(c), limes(v), cont, limes(len(ext)),
           num(len(ext)), plural(len(ext), 'square'), cont, 'that square must be a lime' if len(ext) == 1 else 'those squares must all be limes'))
    if p['nbrs_out'] and any(A(x) in step['cells'] for x in p['nbrs_out']):
        txt += (' That also means every lime of %s is inside %s, so its %s outside it must be empty (also yellow).' % (
            c, cont, plural(len(p['nbrs_out']), 'neighbor')))
    return txt

def src_phrase(src, N, group_cells):
    """why a group of squares holds at most / at least one lime, from an at-most-1 / at-least-1 source"""
    if src['kind'] == 'cont':
        c = N.cont(src['cont'])
        return '%s already has two limes, so its remaining open squares share its last one' % c
    c = N.clue(src['clue'], src['value'])
    have = len(src['mines'])
    return '%s needs only one more lime among its open neighbors' % c if have else '%s allows just one lime among its neighbors' % c

def caption_atmost1_cont(p, N, step):
    cont = N.cont(p['cont']); grp = p['group']; need = 3 - len(p['mines']); n = len(step['cells'])
    N.add('orange', grp)
    return ('%s still needs %s. The orange squares can hold at most one of them (%s), so the %s other open %s (yellow) must %s.' % (
        cap(cont), limes(need), src_phrase(p['src'], N, grp), num(n), plural(n, 'square'), 'be a lime' if n == 1 else 'all be limes'))

def caption_atmost1_clue(p, N, step):
    c = N.clue(p['clue'], p['value']); grp = p['group']; need = p['value'] - len(p['mines']); n = len(step['cells'])
    N.add('orange', grp)
    return ('%s still needs %s. The orange squares can hold at most one of them (%s), so its %s other open %s (yellow) must %s.' % (
        cap(c), limes(need), src_phrase(p['src'], N, grp), num(n), plural(n, 'neighbor'), 'be a lime' if n == 1 else 'all be limes'))

def caption_atleast1_clue(p, N, step):
    c = N.clue(p['clue'], p['value']); grp = p['group']
    N.add('green', grp)
    txt = ('%s needs just one more lime, and the green squares must hold one (%s). That lime is the clue\'s last, so its other open %s (yellow) must be empty.' % (
        cap(c), src_phrase(p['src'], N, grp), plural(len(step['cells']), 'neighbor')))
    if p['kind'] == 'atleast1-clue-cont':
        cont = N.cont(p['cont'])
        txt = ('The green squares must hold a lime (%s). They all lie in %s, which already has two limes, so that lime is its last one and '
               'the other open %s of %s (yellow) must be empty.' % (src_phrase(p['src'], N, grp), cont, plural(len(step['cells']), 'square'), cont))
    return txt

def caption_atleast1_cont(p, N, step):
    cont = N.cont(p['cont']); grp = p['group']
    N.add('green', grp)
    return ('%s needs one more lime, and the green squares must hold one (%s). That lime is the last one for %s, so its other open %s (yellow) must be empty.' % (
        cap(cont), src_phrase(p['src'], N, grp), cont, plural(len(step['cells']), 'square')))

def caption_jig_bump(p, N, step):
    rows = p['axis'] == 'rows'
    k = p['split']            # the boundary lies after row/column k (1-based: below row k)
    hole_color = 'green' if p['side'] == 'bump' else 'orange'
    bump_color = 'orange' if p['side'] == 'bump' else 'green'
    N.add('green', p['hole'] if p['side'] == 'bump' else p['bump'])
    N.add('orange', p['bump'] if p['side'] == 'bump' else p['hole'])
    n = p['count']
    if rows:
        where, below = ('the top row' if k == 1 else 'the top %s rows' % num(k)), 'below row %d' % k
    else:
        where, below = ('the left column' if k == 1 else 'the left %s columns' % num(k)), 'to the right of column %d' % k
    known = 'green' if p['side'] == 'bump' else 'orange'
    deduced = 'orange' if known == 'green' else 'green'
    return ('%s hold %s, and so do the %s jigsaw shapes that lie mostly inside them. The two areas differ only where those shapes '
            'stick out %s (%s) and where other shapes poke in (%s), so the %s squares and the %s squares must hold the same number '
            'of limes. %s' % (
            cap(where), limes(3 * k), num(k), below, bump_color, hole_color, bump_color, hole_color,
            ('The %s squares hold no limes, so neither do the %s and yellow squares: the yellow ones are empty.' % (known, deduced)) if n == 0 else
            ('The %s squares hold %s, so the %s and yellow squares must too: %s.' % (known, limes(n), deduced,
             'the yellow ones are empty' if step['cmd'] == 'CLEAR' else 'the yellow ones must be limes'))))

# ---- subgroup captions ------------------------------------------------------------------
# A group is a set of squares with a bound: 'at-least' N or 'at-most' N limes. Base groups come
# from a container or a clue; derived groups from the interactions in solve_PR.rule_subgroups.
# explain_group() writes the sentences that establish the bound for `label` (the phrase the
# caption uses for the group's squares), one level of derivation deep; beyond that it says
# so rather than nesting parentheses.
def bound_word(g):
    return 'at least' if g['kind'] == 'at-least' else 'at most'

def base_sentence(g, N, label):
    src = g['src']; k = src['kind']; o = g['ord']; least = g['kind'] == 'at-least'
    if k == 'cont':
        c = N.cont(src['cont'])
        if least:
            return '%s still needs %s, and %s are its only open squares.' % (cap(c), limes(o), label)
        if o == 0:
            return '%s already has all three of its limes, and %s are among its open squares.' % (cap(c), label)
        return '%s can take at most %s more, and %s are among its open squares.' % (cap(c), limes(o), label)
    if k == 'clue':
        c = N.clue(src['clue'], src['value'])
        if least:
            return '%s still needs %s among its open neighbors, and %s are all of them.' % (cap(c), limes(o), label)
        if o == 0:
            return '%s already has all of its limes, and %s are among its open neighbors.' % (cap(c), label)
        return '%s can take at most %s more, and %s are among its open neighbors.' % (cap(c), limes(o), label)
    if k == 'jig-lines':
        axis = 'rows' if src['axis'] == 'rows' else 'columns'
        lines = [l + 1 for l in src['lines']]
        shapes = [N.cont(j) for j in src['jigs']]
        n_lines = lines[-1] - lines[0] + 1
        return ('%s %d to %d hold %s in all, and %s %s entirely inside them and %s %s of those. So the other open squares of those %s, '
                'of which %s are %s, hold exactly %s.' % (
                cap(axis), lines[0], lines[-1], limes(3 * n_lines), join_and(shapes), 'lies' if len(shapes) == 1 else 'lie',
                'takes' if len(shapes) == 1 else 'take', limes(3 * len(shapes)), axis, label, 'part' if len(shapes) else 'part', limes(o)))
    return '%s must hold %s %s.' % (cap(label), bound_word(g), limes(o))

def explain_group(g, groups, N, label, depth=0, aux='orange'):
    # aux: the color used for the auxiliary squares an explanation needs (the squares outside
    # a clue's neighborhood, the squares shared with an at-most group); a caption that already
    # uses orange for something else passes 'gray'
    src = g.get('src') or {}
    k = src.get('kind')
    o = g['ord']
    if k in ('cont', 'clue', 'jig-lines'):
        return base_sentence(g, N, label)
    if depth >= 1 or not k:
        return '%s must hold %s %s (this follows from combining the surrounding clues and regions).' % (cap(label), bound_word(g), limes(o))
    if k == 'intersect':
        parent = groups[src['parent']]; outside = src.get('outside', [])
        N.add(aux, outside)
        s1 = explain_group(parent, groups, N, '%s and the %s %s' % (label, aux, plural(len(outside), 'square')), depth + 1, aux)
        return '%s At most %s of those limes can go in the %s %s, so at least %s must be in %s.' % (
            s1, num(len(outside)), aux, plural(len(outside), 'square'), num(o), label)
    if k == 'atleast-minus-atmost':
        outer, inner = groups[src['outer']], groups[src['inner']]
        shared = [c for c in inner['cells'] if c in outer['cells']]
        N.add(aux, shared)
        s1 = explain_group(outer, groups, N, '%s and the %s %s' % (label, aux, plural(len(shared), 'square')), depth + 1, aux)
        s2 = explain_group(inner, groups, N, 'the %s %s' % (aux, plural(len(shared), 'square')), depth + 1, aux)
        return '%s %s So at most %s of the needed limes can be %s, and at least %s must be in %s.' % (
            s1, s2, num(inner['ord']), aux, num(o), label)
    if k == 'atmost-minus-atleast':
        outer, inner = groups[src['outer']], groups[src['inner']]
        N.add('green', inner['cells'])
        s1 = explain_group(outer, groups, N, '%s and the green %s' % (label, plural(len(inner['cells']), 'square')), depth + 1)
        s2 = explain_group(inner, groups, N, 'the green %s' % plural(len(inner['cells']), 'square'), depth + 1)
        return '%s %s That leaves at most %s for %s.' % (s1, s2, limes(o), label)
    return '%s must hold %s %s.' % (cap(label), bound_word(g), limes(o))

def caption_sg_mines(p, N, step):
    groups = p['groups']; g = groups[p['group']]
    n = len(g['cells'])
    label = 'the yellow square' if n == 1 else 'the yellow squares'
    why = explain_group(g, groups, N, label)
    return '%s There %s exactly %s of them, so %s.' % (
        why, 'is' if n == 1 else 'are', num(n), 'it must be a lime' if n == 1 else 'they must all be limes')

def caption_sg_clear_zero(p, N, step):
    groups = p['groups']; g = groups[p['group']]
    n = len(g['cells'])
    label = 'the yellow square' if n == 1 else 'the yellow squares'
    return '%s So %s empty.' % (explain_group(g, groups, N, label), 'it is' if n == 1 else 'they are all')

def caption_sg_clear_subset(p, N, step):
    groups = p['groups']; gl = groups[p['atleast']]; gm = groups[p['atmost']]
    rest = [c for c in gm['cells'] if c not in gl['cells']]
    N.add('green', gl['cells'])
    ng = len(gl['cells']); nr = len(rest)
    s1 = explain_group(gl, groups, N, 'the green %s' % plural(ng, 'square'), aux='orange')
    derived = (gm.get('src') or {}).get('kind') not in ('cont', 'clue', 'jig-lines')
    s2 = explain_group(gm, groups, N, 'the green and yellow squares together', depth=1 if derived else 0, aux='gray')
    return '%s %s The green %s use%s up that whole allowance, so the yellow %s must be empty.' % (
        s1, s2, plural(ng, 'square'), 's' if ng == 1 else '', plural(nr, 'square'))

CAPTIONS = {
    'cont-full': caption_cont_full, 'cont-empties': caption_cont_empties,
    'clue-full': caption_clue_full, 'clue-empties': caption_clue_empties,
    'greedy': caption_greedy, 'greedy-general': caption_greedy_general, 'pushy': caption_pushy,
    'atmost1-cont': caption_atmost1_cont, 'atmost1-clue': caption_atmost1_clue,
    'atleast1-clue': caption_atleast1_clue, 'atleast1-clue-cont': caption_atleast1_clue, 'atleast1-cont': caption_atleast1_cont,
    'jig-bump': caption_jig_bump,
    'sg-mines': caption_sg_mines, 'sg-clear-zero': caption_sg_clear_zero,
    'sg-clear-subset': caption_sg_clear_subset, 'sg-clear-diff': caption_sg_clear_subset,
}

# ---------------------------------------------------------------------------------------
# grouping the log into steps
# ---------------------------------------------------------------------------------------
def step_key(e):
    p = e['prov'] or {}
    k = p.get('kind')
    if k in ('cont-full', 'cont-empties', 'atleast1-cont'):
        return (e['pass'], k, p['cont'], tuple(p.get('group', ())))
    if k in ('clue-full', 'clue-empties', 'atmost1-clue', 'atleast1-clue'):
        return (e['pass'], k, p['clue'], tuple(p.get('group', ())))
    if k == 'atleast1-clue-cont':
        return (e['pass'], k, p['clue'], p['cont'], tuple(p['group']))
    if k == 'atmost1-cont':
        return (e['pass'], k, p['cont'], tuple(p['group']))
    if k in ('greedy', 'pushy'):
        return (e['pass'], k, p['clue'], p['cont'])
    if k == 'greedy-general':
        return (e['pass'], k, p['clue'], p['cont_force'], p['cont_rest'])
    if k == 'jig-bump':
        return (e['pass'], k, p['axis'], p['split'], p['side'], e['cmd'])
    if k in ('sg-mines', 'sg-clear-zero'):
        return (e['pass'], k, p['group'])
    if k in ('sg-clear-subset', 'sg-clear-diff'):
        return (e['pass'], k, p['atmost'], p['atleast'])
    return (e['pass'], k, id(p))

def build_steps(rec, board):
    steps = []
    by_key = {}
    for e in board.log:
        k = step_key(e)
        if k not in by_key:
            by_key[k] = {'entries': [], 'prov': e['prov'], 'rule': e['rule'], 'pass': e['pass']}
            steps.append(by_key[k])
        by_key[k]['entries'].append(e)
    # the pushy rule logs its mines and its corollary clears under one key: keep them one step
    mines, empties = [], []
    out = []
    for i, st in enumerate(steps):
        cells = [A(e['addr']) for e in st['entries']]
        new_mines = [A(e['addr']) for e in st['entries'] if e['cmd'] == 'MINE']
        new_empties = [A(e['addr']) for e in st['entries'] if e['cmd'] == 'CLEAR']
        mines.extend(new_mines); empties.extend(new_empties)
        N = Naming(board, rec.puzzle_type)
        p = st['prov'] or {}
        info = {'cells': cells, 'cmd': 'MINE' if new_mines and not new_empties else ('CLEAR' if new_empties and not new_mines else 'BOTH')}
        fn = CAPTIONS.get(p.get('kind'))
        try:
            caption = fn(p, N, info) if fn else 'Lorem ipsum: no caption for %s.' % p.get('kind')
            caption = N.finish(caption)
        except Exception as ex:
            import traceback; traceback.print_exc()
            caption = 'Caption error (%s): %s' % (p.get('kind'), ex)
        rec_out = {'step': i + 1, 'rule': st['rule'], 'kind': p.get('kind'),
                   'mines': ','.join(mines), 'empties': ','.join(empties), 'hi4s': ','.join(cells), 'caption': caption}
        rec_out.update(N.out(exclude=cells))
        out.append(rec_out)
    out.append({'step': len(out) + 1, 'mines': ','.join(mines), 'empties': ','.join(empties), 'caption': 'Ta-da!'})
    return out

def make_record(ptype, clues, layout=None, answer=None, nom='Literal'):
    if 'jig' in ptype:
        lay = JiggyLayout(9, ptype, layoutInit=layout)
    else:
        lay = Layout(9, ptype)
    return PuzzleRecord(clues, lay, ptype, nom=nom, answer_string=answer if answer else None)

def solve_steps(rec):
    sol, ann = solve_PR.solve(rec, options={'log_steps': True})
    board = rec.board
    steps = build_steps(rec, board)
    solved = sol is not None and len(sol) == 81 and '?' not in sol
    return {'puzzleID': rec.nom,
            'puzz_data': {'version': VERSION, 'gw': 9, 'gh': 9, 'type': rec.puzzle_type, 'clues': rec.clues_string,
                          'layout': rec.layout.layout, 'answer': sol if solved else '',
                          'work': ann.get('work'), 'tier': ann.get('mta'), 'puzzleID': rec.nom},
            'steps': steps}

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--type', default='lime', help='puzzle type: lime, lime-jigsaw, lime-windows, lime-diagonals, lime-centerdot, lime-jigsaw-windows')
    ap.add_argument('--clues', help='81 characters: digits and dots')
    ap.add_argument('--layout', help='81 letters, jigsaw types only')
    ap.add_argument('--answer', help='81 characters of O and . (optional, checked)')
    ap.add_argument('--id', default='Literal', help='puzzle id to echo back')
    ap.add_argument('--file', help='read the puzzle from a puzzle file instead')
    ap.add_argument('--index', type=int, default=1, help='1-based puzzle number in --file')
    ap.add_argument('--text', action='store_true', help='print the captions instead of JSON')
    a = ap.parse_args()
    if a.file:
        n = 0
        for line in open(a.file):
            line = line.strip()
            if not line or line.startswith('#'): continue
            n += 1
            if n == a.index:
                rec = PuzzleRecord.parse_puzzle(line)
                break
        else:
            sys.exit('no puzzle %d in %s' % (a.index, a.file))
    else:
        if not a.clues or len(a.clues) != 81:
            sys.exit('--clues must be 81 characters')
        rec = make_record(a.type, a.clues, a.layout, a.answer, a.id)
    out = solve_steps(rec)
    if a.text:
        print('%s  type=%s  work=%s tier=%s  %s' % (out['puzzleID'], out['puzz_data']['type'], out['puzz_data']['work'], out['puzz_data']['tier'],
                                                  'solved' if out['puzz_data']['answer'] else 'UNSOLVED'))
        for s in out['steps']:
            print('%2d [%s] %s | %s' % (s['step'], s.get('rule', ''), s.get('hi4s', ''), s['caption']))
    else:
        print(json.dumps(out))
