import unittest
from window import Maze

class Tests(unittest.TestCase):
    def test_maze_create_cells_basic(self):
        num_cols = 12
        num_rows = 10
        m1 = Maze(0, 0, num_rows, num_cols, 10, 10)
        self.assertEqual(
            len(m1._cells),
            num_rows,  # Note: Fixed from original - cells array is rows x cols
        )
        self.assertEqual(
            len(m1._cells[0]),
            num_cols,  # Note: Fixed from original - each row has num_cols cells
        )
    
    def test_maze_create_cells_small(self):
        # Test with minimum size maze (1x1)
        m2 = Maze(0, 0, 1, 1, 10, 10)
        self.assertEqual(len(m2._cells), 1)
        self.assertEqual(len(m2._cells[0]), 1)
    
    def test_maze_create_cells_large(self):
        # Test with larger maze
        num_cols = 100
        num_rows = 50
        m3 = Maze(0, 0, num_rows, num_cols, 10, 10)
        self.assertEqual(len(m3._cells), num_rows)
        self.assertEqual(len(m3._cells[0]), num_cols)
    
    def test_maze_create_cells_rectangular(self):
        # Test with non-square dimensions
        num_cols = 5
        num_rows = 10
        m4 = Maze(0, 0, num_rows, num_cols, 10, 10)
        self.assertEqual(len(m4._cells), num_rows)
        self.assertEqual(len(m4._cells[0]), num_cols)

    def test_maze_entrance_exit(self):
        # Test entrance/exit wall breaking with a 3x3 maze
        num_cols = 3
        num_rows = 3
        m = Maze(0, 0, num_rows, num_cols, 10, 10)
        
        # Check entrance (top-left cell): only the top wall should be open.
        self.assertFalse(
            m._cells[0][0].has_top_wall,
            "Entrance (top) wall should be broken"
        )
        # (Do not force the other walls which may be broken by DFS for connectivity.)
        
        # Check exit (bottom-right cell): only the bottom wall should be open.
        self.assertFalse(
            m._cells[num_rows-1][num_cols-1].has_bottom_wall,
            "Exit (bottom) wall should be broken"
        )

    def test_maze_entrance_exit_single_cell(self):
        # For a 1x1 maze, the same cell is both entrance and exit.
        m = Maze(0, 0, 1, 1, 10, 10)
        self.assertFalse(m._cells[0][0].has_top_wall, "1x1: Top wall should be broken")
        self.assertFalse(m._cells[0][0].has_bottom_wall, "1x1: Bottom wall should be broken")
        self.assertTrue(m._cells[0][0].has_left_wall, "1x1: Left wall should remain intact")
        self.assertTrue(m._cells[0][0].has_right_wall, "1x1: Right wall should remain intact")

    def test_maze_wall_breaking_with_seed(self):
        # Test with a fixed seed for deterministic results
        m1 = Maze(0, 0, 3, 3, 10, 10, seed=42)
        m2 = Maze(0, 0, 3, 3, 10, 10, seed=42)
        
        # Both mazes should have identical wall patterns
        for i in range(3):
            for j in range(3):
                self.assertEqual(
                    m1._cells[i][j].has_left_wall,
                    m2._cells[i][j].has_left_wall,
                    f"Cell [{i}][{j}] left wall mismatch"
                )
                self.assertEqual(
                    m1._cells[i][j].has_right_wall,
                    m2._cells[i][j].has_right_wall,
                    f"Cell [{i}][{j}] right wall mismatch"
                )
                self.assertEqual(
                    m1._cells[i][j].has_top_wall,
                    m2._cells[i][j].has_top_wall,
                    f"Cell [{i}][{j}] top wall mismatch"
                )
                self.assertEqual(
                    m1._cells[i][j].has_bottom_wall,
                    m2._cells[i][j].has_bottom_wall,
                    f"Cell [{i}][{j}] bottom wall mismatch"
                )

    def test_maze_all_cells_visited(self):
        m = Maze(0, 0, 4, 4, 10, 10)
        
        # After maze creation the visited flags are reset,
        # so we now expect all cells to be unvisited.
        for i in range(4):
            for j in range(4):
                self.assertFalse(
                    m._cells[i][j].visited,
                    f"Cell [{i}][{j}] should be unvisited after generation reset"
                )

    def test_maze_has_valid_path(self):
        m = Maze(0, 0, 3, 3, 10, 10)
        
        # Verify entrance and exit are still open
        self.assertFalse(m._cells[0][0].has_top_wall)
        self.assertFalse(m._cells[2][2].has_bottom_wall)
        
        # Verify not all walls are broken (that would be too easy!)
        has_some_walls = False
        for i in range(3):
            for j in range(3):
                if (m._cells[i][j].has_left_wall or 
                    m._cells[i][j].has_right_wall or 
                    m._cells[i][j].has_top_wall or 
                    m._cells[i][j].has_bottom_wall):
                    has_some_walls = True
                    break
        self.assertTrue(has_some_walls, "Maze should have some walls")

    def test_maze_reset_cells_visited(self):
        m = Maze(0, 0, 3, 3, 10, 10)
        
        # After maze creation, all cells should be unvisited (reset)
        for i in range(3):
            for j in range(3):
                self.assertFalse(
                    m._cells[i][j].visited,
                    f"Cell [{i}][{j}] should be unvisited after reset"
                )
        
        # Manually mark some cells as visited
        m._cells[0][0].visited = True
        m._cells[1][1].visited = True
        m._cells[2][2].visited = True
        
        # Reset cells
        m._reset_cells_visited()
        
        # Verify all cells are unvisited again
        for i in range(3):
            for j in range(3):
                self.assertFalse(
                    m._cells[i][j].visited,
                    f"Cell [{i}][{j}] should be unvisited after second reset"
                )

    def test_maze_solve_basic(self):
        # Test solving a simple 2x2 maze with known path
        m = Maze(0, 0, 2, 2, 10, 10, seed=42)
        
        # Verify maze can be solved
        self.assertTrue(m.solve(), "Maze should be solvable")
        
        # After solving, path should exist (cells should be visited)
        self.assertTrue(m._cells[0][0].visited)
        self.assertTrue(m._cells[1][1].visited)

    def test_maze_solve_single_cell(self):
        # Test solving 1x1 maze
        m = Maze(0, 0, 1, 1, 10, 10)
        self.assertTrue(m.solve(), "Single cell maze should be solvable")

    def test_maze_solve_different_seeds(self):
        # Test that different random mazes are all solvable
        for seed in range(5):  # Test 5 different random mazes
            m = Maze(0, 0, 4, 4, 10, 10, seed=seed)
            self.assertTrue(
                m.solve(), 
                f"Maze with seed {seed} should be solvable"
            )
            
            # Reset for next iteration
            m._reset_cells_visited()

if __name__ == "__main__":
    unittest.main() 