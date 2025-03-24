#!/usr/bin/env python
"""
generate_gifs.py

Generates animated GIF demos of the maze generation and solving process
for various maze sizes. The animation captures each drawing step by patching
the Maze._animate method.
"""

import os
from PIL import Image, ImageGrab
from window import Maze, Window  # Import the Maze and Window classes

# Global list to store captured frames.
frames = []

def get_canvas_image(win):
    """
    Capture the current Tkinter canvas as a PIL image using ImageGrab.
    Force a full update to ensure the canvas's size and position are current.
    """
    # Force a full update to capture current geometry.
    win._Window__root.update()
    canvas = win._Window__canvas
    x = canvas.winfo_rootx()
    y = canvas.winfo_rooty()
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    bbox = (x+10, y-25, x + w+310, y + h+320)
    img = ImageGrab.grab(bbox)
    return img

# Save the original Maze._animate method.
original_animate = Maze._animate

def patched_animate(self):
    """
    Replacement for Maze._animate that calls the original animate behavior,
    then captures the canvas image for GIF creation.
    """
    original_animate(self)
    img = get_canvas_image(self._win)
    frames.append(img)

# Replace the original animate with our patched version.
Maze._animate = patched_animate

def generate_gif(num_rows, num_cols, output_filename, seed=None):
    """
    Generates a GIF for a maze with the given dimensions.
    
    The canvas size is hardcoded to a square, and the maze will be drawn within
    a central area that takes up 80% of the canvas in each dimension (with 10% margins
    on each side).
    
    - num_rows, num_cols: Maze grid dimensions.
    - output_filename: Where to save the resulting GIF.
    - seed: Optional seed for deterministic maze generation.
    """
    global frames
    frames = []  # Reset captured frames.
    
    # Ensure the output directory exists.
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    # Hardcode the canvas size (square).
    canvas_size = 600
    # Set margin per side as 10% (total margin=20%).
    margin = int(canvas_size * 0.10)  # e.g., 60 pixels for 600x600 canvas
    # Available area for drawing cells.
    available = canvas_size - 2 * margin  # e.g., 480 pixels
    
    # Compute cell dimensions based on number of columns and rows.
    cell_size_x = available / num_cols
    cell_size_y = available / num_rows
    
    # Create the window with a fixed square dimension and force its position.
    win = Window(canvas_size, canvas_size)
    win._Window__root.geometry(f"{canvas_size}x{canvas_size}+10+10")
    win._Window__root.update_idletasks()
    
    # Create the maze using the computed margin and cell sizes.
    maze = Maze(margin, margin, num_rows, num_cols, cell_size_x, cell_size_y, win, seed)
    
    # Solve the maze (this also triggers _animate calls that capture frames).
    maze.solve()
    
    # Close the window and force destruction to avoid subsequent capture issues.
    win.close()
    win._Window__root.destroy()
    
    # Save captured frames as an animated GIF using Pillow.
    duration = int(1000 / 30)  # 30 fps gives ~33ms per frame
    frames[0].save(
        output_filename,
        save_all=True,
        append_images=frames[1:],
        optimize=False,
        duration=duration,
        loop=0
    )
    print(f"Saved GIF to {output_filename}")

def main():
    # Generate GIF for a small maze (3x3).
    generate_gif(
        num_rows=3, num_cols=3, 
        output_filename="gifs/small_maze.gif"
    )
    # Generate GIF for a medium maze (4x6).
    generate_gif(
        num_rows=4, num_cols=6, 
        output_filename="gifs/medium_maze.gif"
    )
    # Generate GIF for a large maze (10x10).
    generate_gif(
        num_rows=10, num_cols=10, 
        output_filename="gifs/large_maze.gif"
    )

if __name__ == "__main__":
    main() 