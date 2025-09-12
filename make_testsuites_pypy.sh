# make testsuites w pypy3
pypy3 gen_puzzles.py -n 1000 -s PR -r 1 -mint 1 -maxt 3 -ed -o testsuites/easy_hard_tier_1_to_3_pypy.txt
pypy3 gen_puzzles.py -n 1000 -s PR -r 1 -mint 1 -maxt 3 -ed -pt lime-centerdot -o testsuites/centerdot_pypy.txt
pypy3 gen_puzzles.py -n 1000 -s PR -r 1 -mint 1 -maxt 3 -ed -pt lime-diagonals -o testsuites/diagonals_pypy.txt
pypy3 gen_puzzles.py -n 1000 -s PR -r 1 -mint 1 -maxt 3 -ed -pt lime-windows -o testsuites/windows_pypy.txt
pypy3 gen_puzzles.py -n 1000 -s PR -r 1 -mint 1 -maxt 3 -ed -pt lime-jigsaw -o testsuites/jigsaw_pypy.txt
pypy3 gen_puzzles.py -n 1000 -s PR -r 1 -mint 1 -maxt 3 -ed -pt lime-jigsaw-windows -o testsuites/jigsaw_windows_pypy.txt
pypy3 gen_puzzles.py -n 1000 -s PR -r 1 -maxt 1 -o testsuites/easy_tier_1_pypy.txt
pypy3 gen_puzzles.py -n 1000 -s PR -r 1 -mint 2 -maxt 2 -o testsuites/medium_tier_2_pypy.txt
pypy3 gen_puzzles.py -n 1000 -s PR -r 1 -mint 3 -maxt 3 -o testsuites/hard_tier_3_pypy.txt

