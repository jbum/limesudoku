#!/usr/bin/env python3
"""
Draw Lime Sudoku puzzles as PNG files using pycairo.
"""

"""
Generated with Cursor/Claude. Prompts used for this:
1. Add pycairo to requirements and install it with pip. 
2. Add a new script draw_limesudoku.py.  It contains a function draw_puzzle that receives a filename, a puzzle-string, an optional answer-string.  It renders the puzzle as a PNG file, about 50 pixels per cell with a 50 pixel margin.  If answer string is provided, it shows where the mines are as green filled circles.  The __main__ function renders a sample puzzle to sample_puzzle_render.png, you can take one from the testsuites/testsuite_100.txt file.
3. It's working.  Make the clues a little larger, and more vertically centered
4. Make the outer border, and the lines that demarcate the 3x3 blocks thicker (about 5 pixels).  Make the thinner lines 0.5 pixels and somewhat lighter in color.
  (did a manual tweak here to refine it)
5. Add an optional argument, annotation, which defaults to an empty string.  If provided, render the annotation, centered, beneath the puzzle in a regular Helvetica font.
6. Added hilighting and partial answer rendering
7: Simplified grid lines algorithm
"""

import cairo

show_steps = True

def draw_puzzle(filename, puzzle_string, answer_string=None, annotation="", hilite_addresses=None,width=640,endcap_style=cairo.LINE_CAP_ROUND):
    """
    Draw a Lime Sudoku puzzle as a PNG file.
    
    Args:
        filename: Output PNG filename
        puzzle_string: 81-character string representing the puzzle
        answer_string: Optional 81-character string with 'O' for mines, '.' for empty
        annotation: Optional text to display centered beneath the puzzle
    """
    if len(puzzle_string) != 81:
        raise ValueError("Puzzle string must be 81 characters long")
    
    if answer_string and len(answer_string) != 81:
        raise ValueError("Answer string must be 81 characters long")
    
    # Constants
    MARGIN = width * 0.05
    CELL_SIZE = (width-MARGIN*2)/9
    GRID_SIZE = 9 * CELL_SIZE
    ANNOTATION_HEIGHT = 30 if annotation else 0
    TOTAL_SIZE = round(GRID_SIZE + 2 * MARGIN + ANNOTATION_HEIGHT)
    step_count = 1


    # Create surface and context
    ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''
    if ext == "svg":
        surface = cairo.SVGSurface(filename, TOTAL_SIZE, TOTAL_SIZE)
    elif ext == "pdf":
        surface = cairo.PDFSurface(filename, TOTAL_SIZE, TOTAL_SIZE)
    elif ext == "eps":
        surface = cairo.PSSurface(filename, TOTAL_SIZE, TOTAL_SIZE)
    else:
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, TOTAL_SIZE, TOTAL_SIZE)
    ctx = cairo.Context(surface)
    
    # Set background to transparent
    ctx.set_source_rgba(0,0,0,0)
    ctx.paint()

    # Fill puzzle area with white background
    ctx.set_source_rgb(1, 1, 1)
    ctx.rectangle(MARGIN-4, MARGIN-4, GRID_SIZE+8, GRID_SIZE+8+50)
    ctx.fill()

    if show_steps:
        surface.write_to_png(f"{filename}.step{step_count}.png")
        step_count += 1
    
    # hilight any highlight squares by filling with a very light blue background
    if hilite_addresses:
        ctx.set_source_rgb(0.9, 0.9, 1)
        for idx in hilite_addresses:
            x = idx % 9
            y = idx // 9
            ctx.rectangle(MARGIN + x * CELL_SIZE, MARGIN + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            ctx.fill()
    
    if show_steps:
        surface.write_to_png(f"{filename}.step{step_count}.png")
        step_count += 1

    # Draw thin grid lines (lighter color)
    ctx.set_source_rgb(0.5, 0.5, 0.5)  # Light gray
    ctx.set_line_width(0.5)

    for i in range(1,9):
        if i % 3 == 0: # thick line
            continue
        # horizontal line
        ctx.move_to(MARGIN, MARGIN + i * CELL_SIZE)
        ctx.line_to(MARGIN + GRID_SIZE, MARGIN + i * CELL_SIZE)
        ctx.stroke()
        # vertical line
        ctx.move_to(MARGIN + i * CELL_SIZE, MARGIN)
        ctx.line_to(MARGIN + i * CELL_SIZE, MARGIN + GRID_SIZE)
        ctx.stroke()
        if show_steps:
            surface.write_to_png(f"{filename}.step{step_count}.png")
            step_count += 1


    ctx.set_source_rgb(0, 0, 0)  # Black
    ctx.set_line_width(3)
    ctx.set_line_cap(endcap_style)
    for i in range(0,9+1,3):
        # horizontal line
        ctx.move_to(MARGIN, MARGIN + i * CELL_SIZE)
        ctx.line_to(MARGIN + GRID_SIZE, MARGIN + i * CELL_SIZE)
        ctx.stroke()
        # vertical line
        ctx.move_to(MARGIN + i * CELL_SIZE, MARGIN)
        ctx.line_to(MARGIN + i * CELL_SIZE, MARGIN + GRID_SIZE)
        ctx.stroke()
        if show_steps:
            surface.write_to_png(f"{filename}.step{step_count}.png")
            step_count += 1
    
    # Draw puzzle numbers
    ctx.set_source_rgb(0, 0, 0)
    ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(32)
    
    for i in range(9):
        for j in range(9):
            idx = i * 9 + j
            char = puzzle_string[idx]
            
            if char != '.':
                # Set color: blue if hilite_addresses and idx in it, else black
                if hilite_addresses is not None and idx in hilite_addresses:
                    ctx.set_source_rgb(0, 0, 1)  # Blue
                else:
                    ctx.set_source_rgb(0, 0, 0)  # Black

                # Calculate text position (center of cell)
                x = MARGIN + j * CELL_SIZE + CELL_SIZE / 2
                y = MARGIN + i * CELL_SIZE + CELL_SIZE / 2
                
                # Get text extents for centering
                extents = ctx.text_extents(char)
                text_x = x - extents.width / 2 - extents.x_bearing
                text_y = y - extents.height / 2 - extents.y_bearing
                
                ctx.move_to(text_x, text_y)
                ctx.show_text(char)
    if show_steps:
        surface.write_to_png(f"{filename}.step{step_count}.png")
        step_count += 1
    
    # Draw mines if answer string is provided
    if answer_string:
        ctx.set_source_rgb(0, 0.7, 0)  # Green color for mines
        count_mines = sum(1 for c in answer_string if c == 'O')
        if count_mines < 27:
            ctx.set_source_rgba(0, 0.7, 0, 0.2)  # Green color for mines with alpha 0.2
        for i in range(9):
            for j in range(9):
                idx = i * 9 + j
                if answer_string[idx] == 'O':
                    # Calculate circle center
                    center_x = MARGIN + j * CELL_SIZE + CELL_SIZE / 2
                    center_y = MARGIN + i * CELL_SIZE + CELL_SIZE / 2
                    radius = CELL_SIZE / 4
                    
                    # Draw filled circle
                    ctx.arc(center_x, center_y, radius, 0, 2 * 3.14159)
                    ctx.fill()

    if show_steps:
        surface.write_to_png(f"{filename}.step{step_count}.png")
        step_count += 1


    # Draw annotation if provided
    if annotation:
        ctx.set_source_rgb(0, 0, 0)
        ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(24)
        
        # Calculate text position (centered horizontally, below the puzzle)
        x = TOTAL_SIZE / 2
        y = MARGIN + GRID_SIZE + 24
        
        # Get text extents for centering
        extents = ctx.text_extents(annotation)
        text_x = x - extents.width / 2 - extents.x_bearing
        text_y = y - extents.height / 2 - extents.y_bearing
        
        ctx.move_to(text_x, text_y)
        ctx.show_text(annotation)
        if show_steps:
            surface.write_to_png(f"{filename}.step{step_count}.png")
            step_count += 1
    
    # Write to file
    ext = filename.split('.')[-1].lower()
    if ext == "png":
        surface.write_to_png(filename)
    elif ext == "svg":
        surface.flush()
        surface.finish()
    elif ext == "pdf":
        surface.flush()
        surface.finish()
    elif ext == "eps":
        surface.flush()
        surface.finish()
    else:
        raise ValueError(f"Unsupported file extension: {ext}")


def main():
    """Main function to draw a sample puzzle."""
    # Sample puzzle from testsuite_100.txt (first line)
    sample_puzzle = "..........3.5..........3.3.....4..4........3...3.3...2.4.1..3............2..2...." # puzzle 1
    sample_answer = "..O.O..O.O.O.O.......O..O.O.O.O..O.....OO.O..OO.....O...O..O..O.O...O..OO....O.O." # answer 1
    sample_answer = None # don't draw it
    sample_hilites = None 
    sample_title = "Puzzle #1"
    # sample_puzzle = ".......3..33.................1....3.........21.33...3....4....2........2........." # puzzle 2
    # # sample_answer = ".OO.....O...O..O.OO...OO...O.....O.O..O..O.O..O..OO.....O...OO....OO..O.OO.O....." # full answer 2
    # sample_answer =   "........O........O.........O.......O.......O.................O........O.........." # partial answer 2
    # sample_hilites = [16,24,25,26,37,51,53,54,55,79,80]
    # sample_title = "Puzzle #2"
    # Draw the sample puzzle with annotation
    draw_puzzle("sample_puzzle_render.png", sample_puzzle, sample_answer, sample_title, hilite_addresses=sample_hilites)
    print("Sample puzzle rendered to sample_puzzle_render.png")


if __name__ == "__main__":
    main() 