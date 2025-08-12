import cairo
import numpy as np
import math
import random
import argparse

# optional -style parameter valid values are lime (default), orange, lemon
parser = argparse.ArgumentParser()
parser.add_argument('-s','--style', type=str, default='lime', choices=['lime', 'orange', 'lemon'], help='style of citrus to draw')
parser.add_argument('-w','--width', type=int, default=128, help='width of the image')
parser.add_argument('-o','--output_filename', type=str, default='citrus.png', help='output filename')
parser.add_argument('-ss', '--show_steps', action='store_true', help='show intermediate steps')

args = parser.parse_args()

# Parameters
img_size = args.width
center = img_size // 2
radius = img_size*224/512
nbr_wedges = random.choice([10, 11])
if args.style == 'lime':
    peel_color = (88/255, 133/255, 37/255)      # Peel color (green) #588525
    pith_color = (237/255, 237/255, 212/255)  # Pith color (off-white) #EDEDD4
    meat_color = (177/255, 201/255, 43/255)  # Meat color (lime green) #B1C92B
elif args.style == 'orange':
    peel_color = (247/255, 158/255, 11/255)  # Orange peel color #F79E0B
    pith_color = (242/255, 207/255, 131/255)  # Orange pith color #F2CF83
    meat_color = (232/255, 133/255, 3/255)  # Orange meat color #E88503
elif args.style == 'lemon':
    peel_color = (250/255, 237/255, 52/255)  # Lemon peel color #FAED34
    pith_color = (246/255, 234/255, 193/255)  # Lemon pith color #F6EAC1
    meat_color = (236/255, 194/255, 51/255)  # Lemon meat color #ECC233
debug_color = (1, 0, 0)  # Debug color (red)
shadow_blur = 3*img_size/128 # int(img_size*12/512 + 0.5)
hub_rotation = random.uniform(0, 2 * math.pi)

step_count = 1

# Create a surface and context
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, img_size, img_size)
ctx = cairo.Context(surface)

if args.show_steps:
    surface.write_to_png(f"{args.output_filename}.step{step_count:02d}.png")
    step_count += 1


# Set background to transparent
ctx.set_operator(cairo.OPERATOR_CLEAR)
ctx.paint()
ctx.set_operator(cairo.OPERATOR_OVER)

# Draw drop shadow
shadow_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, img_size, img_size)
shadow_ctx = cairo.Context(shadow_surface)
shadow_radius = radius

# Create shadow
shadow_ctx.set_source_rgba(0, 0, 0, 0.4)
shadow_ctx.arc(center + .5*img_size/128, center + .5*img_size/128, shadow_radius, 0, 2 * math.pi)
shadow_ctx.fill()

# Apply blur to shadow (simulated with multiple circles of decreasing opacity)
for i in range(int(shadow_blur),0,-1):
    blur_radius = shadow_radius + i
    opacity = 0.02
    shadow_ctx.set_source_rgba(0, 0, 0, opacity)
    shadow_ctx.arc(center+i, center + i, blur_radius, 0, 2 * math.pi)
    shadow_ctx.fill()

# Draw shadow on main surface
ctx.set_source_surface(shadow_surface, 0, 0)
ctx.paint()

if args.show_steps:
    surface.write_to_png(f"{args.output_filename}.step{step_count:02d}.png")
    step_count += 1


# Draw outer peel ring
ctx.set_source_rgb(*peel_color)
ctx.arc(center, center, radius, 0, 2 * math.pi)
ctx.fill()

if args.show_steps:
    surface.write_to_png(f"{args.output_filename}.step{step_count:02d}.png")
    step_count += 1


# Draw pith base
pith_radius = radius * 0.92
ctx.set_source_rgb(*pith_color)
ctx.arc(center, center, pith_radius, 0, 2 * math.pi)
ctx.fill()

if args.show_steps:
    surface.write_to_png(f"{args.output_filename}.step{step_count:02d}.png")
    step_count += 1
# pith_blend_passes = 10
# draw a series of thin rings which blend from pith_color to peel_color, starting at pith_radius and expanding by 0.5 each pass.
pith_blend_passes = 3
for i in range(pith_blend_passes):
    blend_radius = pith_radius + i * 1
    ctx.set_source_rgba(*pith_color, 1 - i / pith_blend_passes)
    ctx.arc(center, center, blend_radius, 0, 2 * math.pi)
    ctx.fill()

if args.show_steps:
    surface.write_to_png(f"{args.output_filename}.step{step_count:02d}.png")
    step_count += 1


# Function to convert polar to Cartesian coordinates
def polar_to_cartesian(r, angle):
    return (center + r * math.cos(angle), center + r * math.sin(angle))

# Create randomized segment angles
angle_step = 2 * math.pi / nbr_wedges
angles = [i * angle_step + random.uniform(-0.05, 0.05) for i in range(nbr_wedges)]
angles.sort()

segment_radius = pith_radius * 0.94
hub_radius = segment_radius * 0.10

# Draw each meat segment
for i in range(nbr_wedges): # nbr_wedges
    a0 = angles[i]+hub_rotation
    a1 = angles[(i + 1) % nbr_wedges]+hub_rotation
    if a1 < a0:
        a1 += 2 * math.pi
    mid_a = (a0 + a1) / 2
    a0 = mid_a + (a0-mid_a)*.45
    a1 = mid_a + (a1-mid_a)*.45
    mini_circle_radius = hub_radius*1.25
    tip_pos = polar_to_cartesian(hub_radius+mini_circle_radius, mid_a)
    center_pos = polar_to_cartesian(0, mid_a)
    outer_circle_l_pos = polar_to_cartesian(segment_radius - mini_circle_radius, a0)
    outer_circle_r_pos = polar_to_cartesian(segment_radius - mini_circle_radius, a1)

    ctx.new_path()
    # ctx.move_to(tip_pos[0], tip_pos[1])
    ctx.arc(tip_pos[0], tip_pos[1], mini_circle_radius*0.5, math.pi*0.5+mid_a, math.pi*1.5+mid_a)
    ctx.arc(outer_circle_l_pos[0], outer_circle_l_pos[1], mini_circle_radius, math.pi*1.5+a0, math.pi*2+a0)
    # outer curve will go here, using a larger circle radius
    ctx.arc(center_pos[0], center_pos[1], segment_radius, a0, a1)

    ctx.arc(outer_circle_r_pos[0], outer_circle_r_pos[1], mini_circle_radius, math.pi*0+a1, math.pi*0.5+a1)
    # ctx.arc(inner_circle_pos[0], inner_circle_pos[1], mini_circle_radius, math.pi*0.5+mid_a, math.pi+mid_a)
    ctx.close_path()

    # Fill the segment
    ctx.set_source_rgb(*meat_color)
    ctx.fill()

    if args.show_steps:
        surface.write_to_png(f"{args.output_filename}.step{step_count:02d}.png")
        step_count += 1


nbr_fibers = 100 # 200
# Set fiber color to white with 10% opacity
ctx.set_source_rgba(1, 1, 1, 0.5)
ctx.set_line_width(0.5*img_size/128)

for i in range(nbr_fibers):
    # Base angle with small random variation to make fibers not perfectly radial
    base_angle = random.uniform(0, 2 * math.pi)
    variation = random.uniform(-0.1, 0.1)  # Small angle variation
    fiber_angle = base_angle + variation
    
    # Start from a random point between hub and edge
    fiber_radius = random.uniform(pith_radius * 0.1, pith_radius * 0.825)
    fiber_start = polar_to_cartesian(fiber_radius, fiber_angle)
    
    # End point follows same angle (radial direction)
    fiber_length = random.uniform(10*img_size/512, 30*img_size/512)  # Varying fiber lengths
    fiber_end = polar_to_cartesian(fiber_radius + fiber_length, fiber_angle)
    
    ctx.move_to(fiber_start[0], fiber_start[1])
    ctx.line_to(fiber_end[0], fiber_end[1])
    ctx.stroke()


if args.show_steps:
    surface.write_to_png(f"{args.output_filename}.step{step_count:02d}.png")
    step_count += 1


nbr_pimples = 20
ctx.set_source_rgba(1, 1, 1, 0.25)
ctx.set_line_width(0.5*img_size/128)
for i in range(nbr_pimples):
    ctx.set_source_rgba(1, 1, 1, random.uniform(0.1, 0.5))
    a = random.uniform(0, 2 * math.pi)
    d = random.uniform(pith_radius * 1.05, radius)
    p0 = polar_to_cartesian(d, a)
    # draw a circle at p0 with radius 1
    ctx.arc(p0[0], p0[1], 1*img_size/128, 0, 2 * math.pi)
    ctx.fill()

if args.show_steps:
    surface.write_to_png(f"{args.output_filename}.step{step_count:02d}.png")
    step_count += 1


# Save and display
surface.write_to_png(args.output_filename)

# Optional: display the image
# import subprocess

# subprocess.run(['open', args.output_filename])
