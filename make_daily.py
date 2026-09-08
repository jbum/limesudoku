#!/usr/bin/env python3
"""
make_daily.py - generate the Lime Sudoku DAILY puzzles for krazydad.com/daily/.

One puzzle per calendar day, following a Monday-to-Sunday recipe (variety type
and difficulty per weekday, see RECIPE below). The generator is happiest making
one kind of puzzle at a time, so each weekday is generated into its own file
(with its own random seed), the wanted difficulty band is selected from it, and
the seven selections are interleaved by date into the final file. Puzzle ids
encode the weekday and the date: KD_lime_Mon_YYYYMMDD .. KD_lime_Sun_YYYYMMDD
(the weekday is the 'kind' the website and its stats key on).

    python3 make_daily.py --start 2026-09-07 --weeks 105

The random seed comes from the start date (20260907 here; --seed overrides),
so a run is reproducible from its file name alone.

Restocking later: run it again with the next start Monday and the same
recipe; all file names carry the start date, so nothing collides, and
every earlier daily file (plus the whole /play/ collection) is part of the
duplicate check.

Files (in puzzledata/daily/):
    lime-daily-<start>-<dow>-<type>-t<tier>.tsv   raw generator output per weekday (oversampled)
    lime-daily-<start>.tsv         the selected, date-ordered puzzles, ready for
                                   upload_daily.py; nom = the puzzle id
Existing files are reused (delete one to regenerate it).
"""

import argparse, os, sys, glob, json, subprocess, datetime, statistics, time
from puzzle_record import PuzzleRecord

DOW = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

# The weekday recipe. 'tier' is the solver rule tier the puzzle needs (1 easy,
# 2 medium, 3 hard); 'work' an optional (min, max) band on the solver's work
# measure, to trim the spread within a tier (tier 2 spans roughly 30-340,
# tier 3 70-580). Anything outside the band is generated but not selected, so
# 'oversample' (default: --oversample) must leave enough headroom.
RECIPES = {
    # the type ramp of the interim /play/ mapping, everything easy
    'flat': {
        'mon': {'ptype': 'lime',                'tier': 1},
        'tue': {'ptype': 'lime-centerdot',      'tier': 1},
        'wed': {'ptype': 'lime-diagonals',      'tier': 1},
        'thu': {'ptype': 'lime-windows',        'tier': 1},
        'fri': {'ptype': 'lime-jigsaw',         'tier': 1},
        'sat': {'ptype': 'lime-jigsaw-windows', 'tier': 1},
        'sun': {'ptype': 'lime-jigsaw-windows', 'tier': 1},
    },
    # type ramp plus a difficulty ramp: easy Mon-Wed, medium Thu-Sat, hard Sun
    'ramp': {
        'mon': {'ptype': 'lime',                'tier': 1},
        'tue': {'ptype': 'lime-centerdot',      'tier': 1},
        'wed': {'ptype': 'lime-diagonals',      'tier': 1},
        'thu': {'ptype': 'lime-windows',        'tier': 2, 'work': (0, 150),   'oversample': 3},
        'fri': {'ptype': 'lime-jigsaw',         'tier': 2, 'work': (0, 180),   'oversample': 3},
        'sat': {'ptype': 'lime-jigsaw-windows', 'tier': 2, 'work': (60, 220),  'oversample': 3},
        'sun': {'ptype': 'lime-jigsaw-windows', 'tier': 3, 'work': (0, 340),   'oversample': 2.5},
    },
}

parser = argparse.ArgumentParser(description='Generate daily Lime Sudoku puzzles')
parser.add_argument('--start', required=True, help='first date, a Monday (YYYY-MM-DD)')
parser.add_argument('--weeks', type=int, default=105, help='number of weeks (default %(default)s = 2 years)')
parser.add_argument('--seed', type=int, help='base random seed (default: the start date as YYYYMMDD)')
parser.add_argument('--recipe', default='ramp', choices=sorted(RECIPES), help='weekday recipe (default %(default)s)')
parser.add_argument('--oversample', type=float, default=2.0, help='generate this many times the puzzles needed per weekday (default %(default)s)')
parser.add_argument('--out-dir', default='puzzledata/daily')
parser.add_argument('--python', default='pypy3', help='interpreter for gen_puzzles.py (default %(default)s)')
parser.add_argument('-v', '--verbose', action='store_true')
args = parser.parse_args()

start = datetime.date.fromisoformat(args.start)
if start.weekday() != 0:
    sys.exit(f'--start {args.start} is a {start.strftime("%A")}, not a Monday')
recipe = RECIPES[args.recipe]
if args.seed is None:
    args.seed = int(start.strftime('%Y%m%d'))
os.makedirs(args.out_dir, exist_ok=True)
final_file = os.path.join(args.out_dir, f'lime-daily-{args.start}.tsv')
if os.path.exists(final_file):
    sys.exit(f'{final_file} already exists; delete it to rebuild')

# Seeds: one per weekday, spread out from the base (the start date) so no two
# weekdays, and no two restocks, share a stream. The old book generators
# used 585226637*v + 434009753*t; these are nowhere near those.
def seed_for(dow_index):
    return (args.seed * 7919 + dow_index * 104729 + 1) % (2**31 - 1)

# ---- 1. generate each weekday's file (oversampled, in generation order) ----
per_weekday = args.weeks
t0 = time.time()
def raw_file(dow, r):
    return os.path.join(args.out_dir, f'lime-daily-{args.start}-{dow}-{r["ptype"]}-t{r["tier"]}.tsv')
for di, dow in enumerate(DOW):
    r = recipe[dow]
    n_gen = int(per_weekday * r.get('oversample', args.oversample) + 0.5)
    fname = raw_file(dow, r)
    if os.path.exists(fname):
        print(f'{dow}: {fname} exists, reusing')
        continue
    cmd = (f'{args.python} gen_puzzles.py -pt {r["ptype"]} -r {seed_for(di)} -n {n_gen} '
           f'-mint {r["tier"]} -maxt {r["tier"]} -sort none -o {fname}')
    print(f'{dow}: {cmd}')
    subprocess.check_call(cmd, shell=True)
    print(f'     done in {time.time() - t0:.0f}s total')

# ---- 2. the duplicate pool: every answer already published or generated ----
def answers_in(fname):
    out = set()
    for line in open(fname):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        try:
            out.add(PuzzleRecord.parse_puzzle(line).answer_string)
        except ValueError:
            pass
    return out

pool = set()
pool_files = sorted(glob.glob('puzzledata/*.tsv')) + \
             sorted(f for f in glob.glob(os.path.join(args.out_dir, 'lime-daily-????-??-??.tsv'))
                    if not f.endswith(f'-{args.start}.tsv'))   # earlier restocks' final files
for f in pool_files:
    pool |= answers_in(f)
print(f'duplicate pool: {len(pool)} answers from {len(pool_files)} files')

# ---- 3. select each weekday's puzzles: in band, not a duplicate ----
selected = {}
for di, dow in enumerate(DOW):
    r = recipe[dow]
    lo, hi = r.get('work', (0, 10**9))
    fname = raw_file(dow, r)
    picks, rejected_band, rejected_dup = [], 0, 0
    for line in open(fname):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        rec = PuzzleRecord.parse_puzzle(line)
        stats = json.loads(line.split('\t')[-1])
        if stats.get('mta') != r['tier'] or not (lo <= stats['work'] <= hi):
            rejected_band += 1
            continue
        if rec.answer_string in pool:
            rejected_dup += 1
            continue
        pool.add(rec.answer_string)
        picks.append((line, stats))
        if len(picks) == per_weekday:
            break
    works = [s['work'] for _, s in picks]
    clues = [sum(1 for c in l.split('\t')[3 if 'jig' in r['ptype'] else 2] if c != '.') for l, _ in picks]
    print(f'{dow}: {r["ptype"]:20s} tier {r["tier"]} work {lo}-{hi if hi < 10**9 else "inf"}: '
          f'selected {len(picks)}/{per_weekday}, skipped {rejected_band} out of band, {rejected_dup} duplicates'
          + (f'; work min/med/max {min(works)}/{int(statistics.median(works))}/{max(works)}, avg clues {statistics.mean(clues):.1f}' if picks else ''))
    if len(picks) < per_weekday:
        sys.exit(f'{dow}: only {len(picks)} of {per_weekday} puzzles fit; raise --oversample (or widen the band) and delete {fname}')
    selected[dow] = picks

# ---- 4. interleave by date into the final file ----
with open(final_file, 'w') as f:
    f.write(f'# Lime Sudoku dailies {args.start} for {args.weeks} weeks, recipe {args.recipe}, seed {args.seed}\n')
    f.write(f'# Command line: {" ".join(sys.argv)}\n')
    f.write('# nom (= puzzle id) \\t type \\t [layout] \\t clues \\t answer \\t stats\n')
    for w in range(args.weeks):
        for di, dow in enumerate(DOW):
            date = start + datetime.timedelta(days=7 * w + di)
            line, _ = selected[dow][w]
            parts = line.split('\t')
            parts[0] = f'KD_lime_{dow.capitalize()}_{date.strftime("%Y%m%d")}'
            f.write('\t'.join(parts) + '\n')
last = start + datetime.timedelta(days=7 * args.weeks - 1)
print(f'wrote {final_file}: {7 * args.weeks} puzzles, {args.start} .. {last} ({time.time() - t0:.0f}s)')
