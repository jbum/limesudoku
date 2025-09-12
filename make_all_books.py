# make all books
import subprocess, time, sys, os

nbr_volumes = 2
puzzles_per_book = 12
books_per_volume = 100

rand_seeds = [585226637,434009753,710723911]

copyright_years = {1:2025, 2:2025}

# current estimated time for 1 volume: ?
puzz_types = [
    {'nom': 'lime-easy', 'opts':'-mint 1 -maxt 1', 'n':puzzles_per_book*books_per_volume, 'ptype': 'lime'}, # 244 (seconds)
    {'nom': 'lime-med',  'opts':'-mint 2 -maxt 2', 'n':puzzles_per_book*books_per_volume, 'ptype': 'lime'}, # 858
    {'nom': 'lime-hard', 'opts':'-mint 3 -maxt 3', 'n':puzzles_per_book*books_per_volume, 'ptype': 'lime'}, # 5192
    {'nom': 'lime-jigsaw', 'opts':'-mint 1 -maxt 3 -ed', 'n':puzzles_per_book*books_per_volume, 'ptype': 'lime-jigsaw'}, # 4163

    # variety books constucted by interleaving these six intermediate files
    {'nom': 'lime-lvp1', 'opts':'-mint 1 -maxt 3 -ed', 'n':puzzles_per_book*books_per_volume//6, 'ptype': 'lime'}, # 396
    {'nom': 'lime-lvp2', 'opts':'-mint 1 -maxt 3 -ed', 'n':puzzles_per_book*books_per_volume//6, 'ptype': 'lime-centerdot'}, # 381 
    {'nom': 'lime-lvp3', 'opts':'-mint 1 -maxt 3 -ed', 'n':puzzles_per_book*books_per_volume//6, 'ptype': 'lime-diagonals'}, # 313
    {'nom': 'lime-lvp4', 'opts':'-mint 1 -maxt 3 -ed', 'n':puzzles_per_book*books_per_volume//6, 'ptype': 'lime-windows'}, # 462
    {'nom': 'lime-lvp5', 'opts':'-mint 1 -maxt 3 -ed', 'n':puzzles_per_book*books_per_volume//6, 'ptype': 'lime-jigsaw'}, # 708
    {'nom': 'lime-lvp6', 'opts':'-mint 1 -maxt 3 -ed', 'n':puzzles_per_book*books_per_volume//6, 'ptype': 'lime-jigsaw-windows'}, # 
]

print_types = [
    {'nom': 'lime-easy', 'title':'Easy Lime Sudoku <LIME>'},
    {'nom': 'lime-med', 'title':'Medium Lime Sudoku <LIME>'},
    {'nom': 'lime-hard', 'title':'Hard Lime Sudoku <LIME>'},
    {'nom': 'lime-jigsaw', 'title':'Jigsaw Limes Sudoku <LIME>'},
    {'nom': 'lime-variety', 'title':'Variety Lime Sudoku <LIME>', 'popts':'-sv'}, # show variety on each puzzle
]

# make a seperate array for printing

fname_template = "./puzzledata/<NOM>-V<VOL>.tsv"

reformat_script_path = '../utils/sidebyside.py'

reformat_args = (["-s a4 -o sheets", "_a4_sheets"], 
                 ["-s a4 -o booklet", "_a4_booklet"], 
                 ["-s ltr -o sheets", "_ltr_sheets"], 
                 ["-s ltr -o booklet", "_ltr_booklet"])

st = time.time()
for v in range(1,nbr_volumes + 1):
    for t,ptype in enumerate(puzz_types):
        rseed = rand_seeds[0]*v + rand_seeds[1]*t
        ofname = fname_template.replace('<NOM>',ptype['nom']).replace('<PTYPE>',ptype['ptype']).replace('<VOL>',str(v))
        # if file exists, continue
        if os.path.exists(ofname):
            continue
        type_opts = ptype['opts']
        num_puzzles = ptype['n']
        cmd = F'pypy3 gen_puzzles.py -pt {ptype["ptype"]} -r {rseed} -n {num_puzzles} {type_opts} -o {ofname}'
        print(cmd)
        # call command
        subprocess.check_call(cmd, shell=True)

    ofname = F"./puzzledata/lime-variety-V{v}.tsv"
    if not os.path.exists(ofname):
        subprocess.check_call('echo "" >ofname', shell=True)
        for book in range(1,books_per_volume+1):
            ofst = 1 + (book-1)*2
            ofst_end = ofst + 1
            for vi in range(1,6+1):
                ifname = F"./puzzledata/lime-lvp{vi}-V{v}.tsv"
                cmd = F'sed -n "{ofst},{ofst_end}p" {ifname} >> {ofname}'
                print(cmd)
                subprocess.check_call(cmd, shell=True)

# got_some = False
# for v in range(1,nbr_volumes + 1):
#     title = 'Lime Sudoku'
#     for ptype in print_types:
#         ifname = F"./puzzledata/{ptype['nom']}-V{v}.tsv"
#         title = ptype['title']
#         for b in range(1,books_per_volume + 1):
#             subtitle = f"VOLUME {v}, BOOK {b}"
#             ofname = F"./sfiles/{ptype['nom']}-{ptype['nom']}-V{v}-B{b}.pdf"
#             if not os.path.exists(ofname):
#                 print_cmd = f'python3 print_puzzles.py {ifname} -b {b} {ofname} -title "{title}" -subtitle "{subtitle}"'
#                 # python3 print_puzzles.py puzzledata/circle9-variety-V1.tsv -b 20 pdfs/sample_variety_book_20.pdf -title ""
#                 print(print_cmd)
#                 subprocess.check_call(print_cmd, shell=True)
#                 got_some = True

#             for refargs,suffix in reformat_args:
#                 src_file = ofname
#                 dst_file = ofname.replace('.pdf',suffix+'.pdf')
#                 if not os.path.exists(dst_file):
#                     reformat_cmd = F"python3 {reformat_script_path}  {src_file} {dst_file} {refargs}"
#                     print(reformat_cmd)
#                     subprocess.check_call(reformat_cmd, shell=True)
#                     got_some = True

# if got_some:
#     cmd = 'aws --profile krazydad s3 sync ./sfiles/ s3://files.krazydad.com/limesudoku/sfiles/ --no-follow-symlinks --exclude "*" --include "lime*.pdf"'
#     print(cmd)
#     subprocess.check_call(cmd, shell=True)
#     cmd = 'aws --profile krazydad cloudfront create-invalidation --distribution-id E3CUBO4WB1YWWP --paths "/limesudoku/sfiles/*"'
#     print(cmd)
#     subprocess.check_call(cmd, shell=True)



et = time.time() - st
print(F"Total elapsed: {et:.1f} seconds")
