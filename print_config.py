# print_config
# -*- coding: utf-8 -*-

page_width = 612
page_height = 828
author = "Jim Bumgardner"
title = "LIME SUDOKU"
subtitle = "<VARIETY>, VOLUME <VOL>, BOOK <BOOK>"
subject = "Lime Sudoku from krazydad.com"
puzzle_title_font = '/Users/jbum/Documents/publishing/generic_assets/fonts/HelveticaNeue BlackCond.ttf'
puzzle_title_font_size = 18
title_color = 0
puzzle_title_y = 194+10-16
page_title_y = 72
top_margin = 72
right_margin = 72
left_margin = 72
bottom_margin = 72
puzzle_top = 2.9*72-16
puzzle_clue_font = '/Users/jbum/Documents/publishing/generic_assets/fonts/HelveticaNeueBd.ttf'
puzzle_clue_font_size_ratio = 0.8

puzzle_copy_font = '/Users/jbum/Documents/publishing/generic_assets/fonts/HelveticaNeueLt.ttf'
puzzle_instructions_size = 14
puzzle_legalese_size = 10

est_font_height_ratio = 0.73

puzzle_width = 360
puzzle_height = 360

puzzle_atitle_font_size = 12
answer_circle_thick_ratio = 0.1
answers_across = 3
answers_down = 4
answers_top = top_margin
answers_bottom = bottom_margin+72
answers_left = left_margin
answers_right = right_margin
answer_width = 130
answer_height = 130
answer_gapx = (page_width - (answers_left+answers_right) - answers_across*answer_width)/(answers_across-1)
answer_gapy = (page_height - (answers_top+answers_bottom) - answers_down*answer_height)/(answers_down-1)

thin_line_ratio = 0.03
thick_line_ratio = 0.1
thin_line_color = 0.8
thick_line_color = 0

window_color = 0.9
diagonal_line_color = 0.8
diagonal_line_ratio = 0.2

center_dot_color = 0.85

clue_color = 0
cancel_color = 0.5

puzzles_per_book = 12
page_title = "Lime Sudoku, Volume <VOL>, Book <BOOK>"

instructions_top = 598+72/2-8
instructions_lheight = puzzle_instructions_size
instructions = {
    'lime':[
             'Place three limes into each row, column, and 3×3 block.',
             'Numbers indicate the number of adjacent limes surrounding the square.'],
    'lime-centerdot':[
             'Place three limes into each row, column, and 3×3 block.',
             'The shaded center dots also contain 3 limes.',
             'Numbers indicate the number of adjacent limes surrounding the square.'],
    'lime-diagonals':[
             'Place three limes into each row, column, and 3×3 block.',
             'The long diagonals also contain 3 limes.',
             'Numbers indicate the number of adjacent limes surrounding the square.'],
    'lime-windows':[
             'Place three limes into each row, column, 3×3 block, and shaded block.',
             'Numbers indicate the number of adjacent limes surrounding the square.'],
    'lime-jigsaw':[
             'Place three limes into each row, column, and jigsaw shape.',
             'Numbers indicate the number of adjacent limes surrounding the square.'],
    'lime-jigsaw-windows':[
             'Place three limes into each row, column, jigsaw shape, and shaded block.',
             'Numbers indicate the number of adjacent limes surrounding the square.'],
    'citrus':[
             'Place a lime, orange, and lemon into each row, column, and 3×3 block.',
             'Numbers indicate the number of adjacent fruits surrounding the square.'],
}

copyright_string = "©<YEAR> krazydad.com"
