# test suite converter

# convert from this format:
# ..........3.5..........3.3.....4..4........3...3.3...2.4.1..3............2..2....	# ..O.O..O.O.O.O.......O..O.O.O.O..O.....OO.O..OO.....O...O..O..O.O...O..OO....O.O. #1   abc=382.4
# puzzle<tab># answer comments
#
# to tab delimited
# name,puzzle_type[, layout if puzzle_type contains 'jigsaw'], puzzle, solution, comments

import argparse

def main():
    parser = argparse.ArgumentParser(description='Convert test suite from old format to new format')
    parser.add_argument('input_file', type=str, help='Input file')
    parser.add_argument('output_file', type=str, help='Output file')
    args = parser.parse_args()

    puzzles = []
    comment_lines = []
    with open(args.input_file, 'r') as file:
        for line_num, line in enumerate(file, 1):
            line = line.strip()
            
            # Skip empty lines and comment-only lines
            if not line or line.startswith('#'):
                if line.startswith('#'):
                    comment_lines.append(line)
                continue


            if "\tlime" in line:
                # parse my other format
                parts = line.split('\t')
                nom = parts[0]
                parts = parts[1:]
                ptype = parts[0]
                parts = parts[1:]
                if 'jiggy' in ptype:
                    layout = parts[0]
                    parts = parts[1:]
                else:
                    layout = None
                puzzle_str = parts[0]
                parts = parts[1:]
                answer_str = parts[0]
                comment = 'ans='+answer_str
            else:
                # Split on '#' to separate puzzle from comment
                parts = line.split('#', 1)
                puzzle_str = parts[0].strip()[:81]
                answer_str = parts[1][1:82]
                comment = parts[1][83:]
                layout = None
                ptype = 'lime'
            puzzles.append({'puzzle':puzzle_str, 'comment':comment, 'answer':answer_str, 'layout':layout, 'ptype':ptype})
    
    with open(args.output_file, 'w') as file:
        for pi,puzrec in enumerate(puzzles, 1):
            file.write(f"puzzle-{pi}\t{puzrec['ptype']}{"\t"+puzrec['layout'] if puzrec['layout'] else ""}\t{puzrec['puzzle']}\t{puzrec['answer']}\t{puzrec['comment']}\n")
        for comment_line in comment_lines:
            file.write(comment_line + "\n")

if __name__ == "__main__":
    main()