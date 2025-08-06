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
"""

import cairo


def draw_puzzle(filename, puzzle_string, answer_string=None, annotation=""):
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
    CELL_SIZE = 50
    MARGIN = 50
    GRID_SIZE = 9 * CELL_SIZE
    ANNOTATION_HEIGHT = 30 if annotation else 0
    TOTAL_SIZE = GRID_SIZE + 2 * MARGIN + ANNOTATION_HEIGHT
    
    # Create surface and context
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, TOTAL_SIZE, TOTAL_SIZE)
    ctx = cairo.Context(surface)
    
    # Set background to white
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()
    
    # Draw thin grid lines (lighter color)
    ctx.set_source_rgb(0.5, 0.5, 0.5)  # Light gray
    ctx.set_line_width(0.5)
    
    # Draw horizontal lines (skip outer border and 3x3 block lines)
    for i in range(1, 9):
        if i % 3 != 0:  # Skip lines that are 3x3 block boundaries
            y = MARGIN + i * CELL_SIZE
            ctx.move_to(MARGIN, y)
            ctx.line_to(MARGIN + GRID_SIZE, y)
            ctx.stroke()
    
    # Draw vertical lines (skip outer border and 3x3 block lines)
    for i in range(1, 9):
        if i % 3 != 0:  # Skip lines that are 3x3 block boundaries
            x = MARGIN + i * CELL_SIZE
            ctx.move_to(x, MARGIN)
            ctx.line_to(x, MARGIN + GRID_SIZE)
            ctx.stroke()
    
    # Draw thicker lines for outer border and 3x3 blocks
    ctx.set_source_rgb(0, 0, 0)  # Black
    ctx.set_line_width(3)
    
    # Draw outer border
    ctx.rectangle(MARGIN, MARGIN, GRID_SIZE, GRID_SIZE)
    ctx.stroke()
    
    # Draw 3x3 block lines
    for i in range(1, 3):
        # Vertical block lines
        x = MARGIN + i * 3 * CELL_SIZE
        ctx.move_to(x, MARGIN)
        ctx.line_to(x, MARGIN + GRID_SIZE)
        ctx.stroke()
        
        # Horizontal block lines
        y = MARGIN + i * 3 * CELL_SIZE
        ctx.move_to(MARGIN, y)
        ctx.line_to(MARGIN + GRID_SIZE, y)
        ctx.stroke()
    
    # Draw puzzle numbers
    ctx.set_source_rgb(0, 0, 0)
    ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(28)
    
    for i in range(9):
        for j in range(9):
            idx = i * 9 + j
            char = puzzle_string[idx]
            
            if char != '.':
                # Calculate text position (center of cell)
                x = MARGIN + j * CELL_SIZE + CELL_SIZE / 2
                y = MARGIN + i * CELL_SIZE + CELL_SIZE / 2
                
                # Get text extents for centering
                extents = ctx.text_extents(char)
                text_x = x - extents.width / 2 - extents.x_bearing
                text_y = y - extents.height / 2 - extents.y_bearing
                
                ctx.move_to(text_x, text_y)
                ctx.show_text(char)
    
    # Draw mines if answer string is provided
    if answer_string:
        ctx.set_source_rgb(0, 0.7, 0)  # Green color for mines
        
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
    
    # Draw annotation if provided
    if annotation:
        ctx.set_source_rgb(0, 0, 0)
        ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(16)
        
        # Calculate text position (centered horizontally, below the puzzle)
        x = TOTAL_SIZE / 2
        y = MARGIN + GRID_SIZE + 20
        
        # Get text extents for centering
        extents = ctx.text_extents(annotation)
        text_x = x - extents.width / 2 - extents.x_bearing
        text_y = y - extents.height / 2 - extents.y_bearing
        
        ctx.move_to(text_x, text_y)
        ctx.show_text(annotation)
    
    # Write to file
    surface.write_to_png(filename)


def main():
    """Main function to draw a sample puzzle."""
    # Sample puzzle from testsuite_100.txt (first line)
    sample_puzzle = "..........3.5..........3.3.....4..4........3...3.3...2.4.1..3............2..2...."
    sample_answer = "..O.O..O.O.O.O.......O..O.O.O.O..O.....OO.O..OO.....O...O..O..O.O...O..OO....O.O."
    
    # Draw the sample puzzle with annotation
    draw_puzzle("sample_puzzle_render.png", sample_puzzle, sample_answer, "Sample Lime Sudoku Puzzle")
    print("Sample puzzle rendered to sample_puzzle_render.png")


if __name__ == "__main__":
    main() 