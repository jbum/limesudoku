# make testsuites
python3 gen_puzzles.py -n 1000 -s PR -r 1 -maxt 1 -o testsuites/easy_tier_1.txt
python3 gen_puzzles.py -n 1000 -s PR -r 1 -mint 2 -maxt 2 -o testsuites/medium_tier_2.txt
python3 gen_puzzles.py -n 1000 -s PR -r 1 -mint 3 -maxt 3 -o testsuites/hard_tier_3.txt


