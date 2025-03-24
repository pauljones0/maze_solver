from tkinter import Tk, BOTH, Canvas
import time
import random

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
    
    def draw(self, canvas, fill_color):
        canvas.create_line(
            self.p1.x, self.p1.y, self.p2.x, self.p2.y, 
            fill=fill_color, width=2
        )

class Window:
    def __init__(self, width, height):
        self.__root = Tk()
        self.__root.title("Maze Solver")
        self.__canvas = Canvas(self.__root, width=width, height=height)
        self.__canvas.pack(fill=BOTH, expand=1)
        self.__running = False
        self.__root.protocol("WM_DELETE_WINDOW", self.close)
    
    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()

    def wait_for_close(self):
        self.__running = True
        while self.__running:
            self.redraw()

    def close(self):
        self.__running = False

    def draw_line(self, line, fill_color):
        line.draw(self.__canvas, fill_color)

class Cell:
    def __init__(self, win=None):
        self.has_left_wall = True
        self.has_right_wall = True
        self.has_top_wall = True
        self.has_bottom_wall = True
        self.visited = False
        self._x1 = None
        self._x2 = None
        self._y1 = None
        self._y2 = None
        self._win = win
        
    def draw(self, x1, y1, x2, y2):
        self._x1 = x1
        self._x2 = x2
        self._y1 = y1
        self._y2 = y2
        
        if self._win is None:
            return
            
        # Draw all walls, using white for removed walls
        line = Line(Point(x1, y1), Point(x1, y2))
        self._win.draw_line(line, "black" if self.has_left_wall else "#d9d9d9")
        
        line = Line(Point(x1, y1), Point(x2, y1))
        self._win.draw_line(line, "black" if self.has_top_wall else "#d9d9d9")
        
        line = Line(Point(x2, y1), Point(x2, y2))
        self._win.draw_line(line, "black" if self.has_right_wall else "#d9d9d9")
        
        line = Line(Point(x1, y2), Point(x2, y2))
        self._win.draw_line(line, "black" if self.has_bottom_wall else "#d9d9d9")

    def draw_move(self, to_cell, undo=False):
        if self._win is None:
            return
            
        # Calculate center points of both cells
        from_x = (self._x1 + self._x2) // 2
        from_y = (self._y1 + self._y2) // 2
        to_x = (to_cell._x1 + to_cell._x2) // 2
        to_y = (to_cell._y1 + to_cell._y2) // 2
        
        # Draw the line with appropriate color
        line = Line(Point(from_x, from_y), Point(to_x, to_y))
        self._win.draw_line(line, "gray" if undo else "red")

class Maze:
    def __init__(
            self,
            x1,
            y1,
            num_rows,
            num_cols,
            cell_size_x,
            cell_size_y,
            win=None,
            seed=None,
        ):
        if seed is not None:
            random.seed(seed)
            
        self._x1 = x1
        self._y1 = y1
        self._num_rows = num_rows
        self._num_cols = num_cols
        self._cell_size_x = cell_size_x
        self._cell_size_y = cell_size_y
        self._win = win
        self._cells = []
        
        self._create_cells()
        self._break_walls_r(0, 0)  # DFS maze generation
        self._break_entrance_and_exit()  # Open the exterior at entrance/exit
        self._reset_cells_visited()      # Reset visited flags for solving
    
    def _break_walls_r(self, i, j):
        # Set recursion limit for large mazes
        import sys
        sys.setrecursionlimit(10000)
        
        self._cells[i][j].visited = True
        self._draw_cell(i, j)  # Draw cell after marking as visited
        
        while True:
            possible_dirs = []
            
            # Check all adjacent cells (up, right, down, left)
            # Up
            if i > 0 and not self._cells[i-1][j].visited:
                possible_dirs.append((i-1, j, "up"))
            # Right
            if j < self._num_cols-1 and not self._cells[i][j+1].visited:
                possible_dirs.append((i, j+1, "right"))
            # Down
            if i < self._num_rows-1 and not self._cells[i+1][j].visited:
                possible_dirs.append((i+1, j, "down"))
            # Left
            if j > 0 and not self._cells[i][j-1].visited:
                possible_dirs.append((i, j-1, "left"))
            
            # If no unvisited neighbors, we're done with this cell
            if len(possible_dirs) == 0:
                return
            
            # Choose random direction and break walls
            next_i, next_j, direction = random.choice(possible_dirs)
            
            if direction == "up":
                self._cells[i][j].has_top_wall = False
                self._cells[next_i][next_j].has_bottom_wall = False
            elif direction == "right":
                self._cells[i][j].has_right_wall = False
                self._cells[next_i][next_j].has_left_wall = False
            elif direction == "down":
                self._cells[i][j].has_bottom_wall = False
                self._cells[next_i][next_j].has_top_wall = False
            elif direction == "left":
                self._cells[i][j].has_left_wall = False
                self._cells[next_i][next_j].has_right_wall = False
            
            # Recursively visit the next cell
            self._break_walls_r(next_i, next_j)
    
    def _create_cells(self):
        # Initialize the grid of cells
        self._cells = [[Cell(self._win) for col in range(self._num_cols)] 
                      for row in range(self._num_rows)]
        
        # Draw each cell
        for i in range(self._num_rows):
            for j in range(self._num_cols):
                self._draw_cell(i, j)
    
    def _draw_cell(self, i, j):
        # Calculate the cell's position
        x1 = self._x1 + j * self._cell_size_x
        y1 = self._y1 + i * self._cell_size_y
        x2 = x1 + self._cell_size_x
        y2 = y1 + self._cell_size_y
        
        # Draw the cell
        self._cells[i][j].draw(x1, y1, x2, y2)
        self._animate()
    
    def _animate(self):
        if self._win is None:
            return
        self._win.redraw()
        # Scale delay exponentially down for larger mazes
        total_cells = self._num_rows * self._num_cols
        delay = min(0.05, 1 / total_cells)
        time.sleep(delay)

    def _reset_cells_visited(self):
        # Reset visited flag for all cells
        for i in range(self._num_rows):
            for j in range(self._num_cols):
                self._cells[i][j].visited = False

    def solve(self):
        self._reset_cells_visited()  # Reset visited flags for solving
        return self._solve_r(0, 0)
    
    def _solve_r(self, i, j):
        self._animate()
        self._cells[i][j].visited = True
        
        # If we reached the end cell (bottom-right)
        if i == self._num_rows - 1 and j == self._num_cols - 1:
            return True
            
        # Try each direction (up, right, down, left)
        # Up
        if (i > 0 and 
            not self._cells[i][j].has_top_wall and 
            not self._cells[i-1][j].visited):
            self._cells[i][j].draw_move(self._cells[i-1][j])
            if self._solve_r(i-1, j):
                return True
            self._cells[i][j].draw_move(self._cells[i-1][j], True)  # undo
            
        # Right
        if (j < self._num_cols - 1 and 
            not self._cells[i][j].has_right_wall and 
            not self._cells[i][j+1].visited):
            self._cells[i][j].draw_move(self._cells[i][j+1])
            if self._solve_r(i, j+1):
                return True
            self._cells[i][j].draw_move(self._cells[i][j+1], True)  # undo
            
        # Down
        if (i < self._num_rows - 1 and 
            not self._cells[i][j].has_bottom_wall and 
            not self._cells[i+1][j].visited):
            self._cells[i][j].draw_move(self._cells[i+1][j])
            if self._solve_r(i+1, j):
                return True
            self._cells[i][j].draw_move(self._cells[i+1][j], True)  # undo
            
        # Left
        if (j > 0 and 
            not self._cells[i][j].has_left_wall and 
            not self._cells[i][j-1].visited):
            self._cells[i][j].draw_move(self._cells[i][j-1])
            if self._solve_r(i, j-1):
                return True
            self._cells[i][j].draw_move(self._cells[i][j-1], True)  # undo
        
        return False

    def _break_entrance_and_exit(self):
        # For a 1x1 maze, remove both top and bottom walls.
        if self._num_rows == 1 and self._num_cols == 1:
            cell = self._cells[0][0]
            cell.has_top_wall = False
            cell.has_bottom_wall = False
            self._draw_cell(0, 0)
        else:
            # For entrance cell (top-left): only remove the top wall.
            self._cells[0][0].has_top_wall = False
            self._draw_cell(0, 0)
            
            # For exit cell (bottom-right): only remove the bottom wall.
            self._cells[self._num_rows-1][self._num_cols-1].has_bottom_wall = False
            self._draw_cell(self._num_rows-1, self._num_cols-1)

def main():
    # Calculate window size based on maze dimensions
    num_rows = 4
    num_cols = 6
    cell_size_x = 50
    cell_size_y = 50
    margin = 50  # Space around the maze
    
    # Calculate total window size
    window_width = (cell_size_x * num_cols) + (margin * 2)
    window_height = (cell_size_y * num_rows) + (margin * 2)
    
    # Create window with calculated dimensions
    win = Window(window_width, window_height)
    
    # Create maze with margin offset to center it
    maze = Maze(margin, margin, num_rows, num_cols, cell_size_x, cell_size_y, win)
    
    # Solve the maze
    maze.solve()
    
    win.wait_for_close()

if __name__ == "__main__":
    main() 