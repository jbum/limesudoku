#!/usr/bin/env python3
"""
upload_daily.py - upload a daily Lime Sudoku file (from make_daily.py) to the
krazydad puzzle API. The puzzle id is the record's nom (KD_lime_<Dow>_YYYYMMDD).

    python3 upload_daily.py puzzledata/daily/lime-daily-2026-09-07.tsv           # everything
    python3 upload_daily.py <file> --from 2026-09-09 --to 2026-09-30            # a date range
    python3 upload_daily.py <file> -d                                           # dry run: print, no upload
    python3 upload_daily.py <file> -t                                           # first 2 only

Re-uploading an id replaces the stored puzzle, so a rerun is safe.
"""

import argparse, re, sys, json, hashlib, subprocess, urllib.parse, pprint
import krazydad_apikey
import krazydad_api_endpoint
from puzzle_record import PuzzleRecord

parser = argparse.ArgumentParser(description='Upload daily Lime Sudoku puzzles')
parser.add_argument('file')
parser.add_argument('--from', dest='date_from', help='first date to upload (YYYY-MM-DD)')
parser.add_argument('--to', dest='date_to', help='last date to upload (YYYY-MM-DD)')
parser.add_argument('-d', '--debug', action='store_true', help='print the payloads, upload nothing')
parser.add_argument('-t', '--test', action='store_true', help='upload the first 2 only')
parser.add_argument('-l', '--limit', type=int, help='upload at most N')
parser.add_argument('--skip', type=int, default=0, help='skip the first N (for retries)')
parser.add_argument('-v', '--verbose', action='store_true')
args = parser.parse_args()
if args.test:
    args.limit = 2

ID_RE = re.compile(r'^KD_lime_(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)_(\d{4})(\d{2})(\d{2})$')
n_seen = n_sent = n_bad = 0
for line in open(args.file):
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    rec = PuzzleRecord.parse_puzzle(line)
    m = ID_RE.match(rec.nom)
    if not m:
        sys.exit(f'not a daily id: {rec.nom!r}')
    date = f'{m[1]}-{m[2]}-{m[3]}'
    if (args.date_from and date < args.date_from) or (args.date_to and date > args.date_to):
        continue
    n_seen += 1
    if n_seen <= args.skip:
        continue
    if args.limit and n_sent >= args.limit:
        break
    puzzle_id = rec.nom
    puzzle_data = {'ptitle': puzzle_id, 'width': 9, 'height': 9, 'type': rec.puzzle_type,
                   'clues_str': rec.clues_string, 'solved': rec.answer_string}
    if 'jig' in rec.puzzle_type:
        puzzle_data['layout'] = rec.layout.layout
    payload = json.dumps(puzzle_data)
    sig = hashlib.sha256((puzzle_id + '_' + krazydad_apikey.kdPutSecret).encode('utf-8')).hexdigest()
    url = '%s/putpuzzle/%s/?sig=%s&comments=&puzzle_data=%s' % (
        krazydad_api_endpoint.KD_API_V3_ENDPOINT, urllib.parse.quote(puzzle_id),
        urllib.parse.quote(sig), urllib.parse.quote(payload))
    n_sent += 1
    if args.debug:
        pprint.pprint(puzzle_data)
        continue
    print('-->', puzzle_id, rec.puzzle_type)
    out, _ = subprocess.Popen(['curl', '--silent', url], stdout=subprocess.PIPE).communicate()
    try:
        result = json.loads(out)
    except ValueError:
        result = {}
    if not result.get('success'):
        n_bad += 1
        print('PROBLEM', out)
print(f'{n_sent} uploaded, {n_bad} problems' if not args.debug else f'{n_sent} would be uploaded')
