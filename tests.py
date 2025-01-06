import unittest
from window import *

class Tests(unittest.TestCase):
    def test_maze_create_cells(self):
        num_cols = 12
        num_rows = 10
        m1 = Maze(0, 0, num_rows, num_cols, 10)
        self.assertEqual(
            len(m1._cells),
            num_cols,
        )
        self.assertEqual(
            len(m1._cells[0]),
            num_rows,
        )
    
    def test_pathatble_between_cells(self):
        num_cols = 12
        num_rows = 10
        m1 = Maze(0, 0, num_rows, num_cols, 10)
        cell1 = m1._cells[0][0]
        cell2 = m1._cells[0][1]
        cell3 = m1._cells[1][0]
        if not cell1.has_walls[cell_walls.BOTTOM]:
            print(f"dafuq: {cell1.has_walls[cell_walls.BOTTOM]}")
            self.assertTrue(m1._cells_are_pathable(0,0,0,1))
        else:
            self.assertFalse(m1._cells_are_pathable(0,0,0,1))
        if not cell1.has_walls[cell_walls.RIGHT]:
            print(f"dafuq: {cell1.has_walls[cell_walls.RIGHT]}")
            self.assertTrue(m1._cells_are_pathable(0,0,1,0))
        else:
            self.assertFalse(m1._cells_are_pathable(0,0,1,0))
        
if __name__ == "__main__":
    unittest.main()