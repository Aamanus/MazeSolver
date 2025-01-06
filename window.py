from constants import *
from tkinter import Tk, BOTH, Canvas
import time
import random
# Holds our draw related classes


class Window():
    def __init__(self, width, height):
        self.__root = Tk()
        self.__root.title("KazaNet Maze Solver")
        self.__root.geometry(f"{width}x{height}")
        self.__running = False
        self.__canvas = Canvas(self.__root, width=width, height=height, bg="black")
        self.__canvas.pack(fill=BOTH, expand=True)
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

    def draw_line(self, line: 'Line', fill_colour: str):
        return line.draw(self.__canvas,fill_colour)
    
    def canvas_delete(self,id):
       self.__canvas.delete(id)

class Cell():
    def __init__(self, x, y, size = CELL_SIZE, window: Window = None):
        self.coords = [Point(x,y),Point(x+size,y)
                       ,Point(x+size,y+size),Point(x,y+size)]
        self.__window = window
        self.size = size
        # status for walls, in order top, right, bottom, left
        self.has_walls = [True,True,True,True]
        self.walls = [Line(self.coords[0],self.coords[1]),
                      Line(self.coords[1],self.coords[2]),
                      Line(self.coords[2],self.coords[3]),
                      Line(self.coords[3],self.coords[0])]
        self._wall_lines = [None for i in range(4)]
        self.center = Point(x+(self.size//2),y+(self.size//2))
        self._visited = False

    def draw_move(self, to_cell, undo=False):
        if self.__window == None:
            return
        fill_colour = "gray" if undo else "red"
        self.__window.draw_line(Line(self.center,to_cell.center),fill_colour)
    
    def draw(self):
        if self.__window == None:
            return
        for i in range(len(self.has_walls)):
            if self.has_walls[i] and self._wall_lines[i] is None:

                self._wall_lines[i] = self.__window.draw_line(self.walls[i],"white")
    
    def break_wall(self,wall,visit = True,debug = False):

        if debug:
            print(f"breaking wall {wall} in cell {self.coords} and will delete {self._wall_lines[wall]}")
        self.has_walls[wall] = False
        if self.__window is not None:
            self.__window.canvas_delete(self._wall_lines[wall])
        self._wall_lines[wall] = None
        if visit:
            self._visited = True

    def visit(self):
        self._visited = True
    
    def unvisit(self):
        self._visited = False
    
    def num_walls(self):
        return sum(self.has_walls)
    
    def is_wall_broken(self,wall):
        return not self.has_walls[wall]


    

                
class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.coords = (x, y)
    
    def __repr__(self):
        return f"Point({self.x},{self.y})"

class Line():
    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1
        self.p2 = p2
        self.coords = (p1.coords, p2.coords)
        self.width = 2
    
    def draw(self, canvas: Canvas, fill_colour):
        return canvas.create_line(self.coords[0][0], self.coords[0][1], 
                           self.coords[1][0], self.coords[1][1],
                           fill=fill_colour, width=self.width)
        

class Maze():
    def __init__(
        self,
        x,
        y,
        num_rows,
        num_cols,
        cell_size,
        win = None,
        seed = None,
    ):
        self.x = x
        self.y = y
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.cell_size = cell_size
        self._win = win
        if seed:
            self.seed = random.seed(seed)
        else:
            self.seed = 0
        
        self._cells = []
        self._create_cells()

        self._break_entrance_and_exit()

        self._break_walls_r(0,0)
        
        self._draw_cell(0,0)
        self._draw_cell(num_rows-1, num_cols-1)

        self._reset_visited()



    def _create_cells(self):
        

        for col in range(self.num_cols):
            col_list = []
            self._cells.append(col_list)
            for row in range(self.num_rows):
                x = self.x + col * self.cell_size
                y = self.y + row * self.cell_size
                col_list.append(Cell(x,y,self.cell_size, self._win))
                self._draw_cell(col,row)
            
            
        
    def _draw_cell(self,col, row):
        if self._win == None:
            return
        self._cells[col][row].draw()
        #self._animate()
        
    
    def _animate(self):
        if self._win == None:
            return
        self._win.redraw()
        time.sleep(0.05)

    def _break_entrance_and_exit(self):
        self._cells[0][0].break_wall(cell_walls.TOP,False)
        self._cells[self.num_cols - 1][self.num_rows - 1].break_wall(cell_walls.BOTTOM,False)
        self._draw_cell(0,0)
        self._draw_cell(self.num_cols - 1, self.num_rows - 1)
        self._animate()

    def _break_walls_r(self,col,row):
        cur_cell = self._cells[col][row]
        cur_cell.visit()
        
        while True:
            to_visit = []
            # check four directions from cell and see if they are visited. If not, add to list
            if col > 0 and not self._cells[col - 1][row]._visited:
                to_visit.append((col - 1, row))
            
            if col < (self.num_cols - 1) and not self._cells[col + 1][row]._visited:
                to_visit.append((col + 1, row))
            
            if row > 0 and not self._cells[col][row-1]._visited:
                to_visit.append((col, row - 1))
            
            if row < (self.num_rows - 1) and not self._cells[col][row+1]._visited:
                to_visit.append((col, row + 1))
            
            if len(to_visit) == 0:
                # No cells to visit, so just return

                return
            
            next = to_visit[random.randint(0,len(to_visit)-1)]
            self._break_walls_between_cells(col,row,next[0],next[1])
            
            self._break_walls_r(next[0],next[1])
            #draw our current cell regardless
            


    def _break_walls_between_cells(self, col1, row1, col2, row2):
        # Check if the two cells are adjacent

        if abs(col1 - col2) + abs(row1 - row2) != 1:
            return
        # Check if the two cells are the same
        if col1 == col2 and row1 == row2:
            return
        debug = False


        # Check if the two cells are in the same row
        if row1 == row2:
            #They are! So we break walls horizontally between the 2 after finding the left cell
            if col1 < col2:
                self._cells[col2][row1].break_wall(cell_walls.LEFT,True)
                self._cells[col1][row1].break_wall(cell_walls.RIGHT,True)
            else:
                self._cells[col1][row1].break_wall(cell_walls.LEFT,True)
                self._cells[col2][row1].break_wall(cell_walls.RIGHT,True)
        else:
            #They are not! So we break walls vertically between the 2 after finding the top cell
            if row1 < row2:
                self._cells[col1][row2].break_wall(cell_walls.TOP,True)
                self._cells[col1][row1].break_wall(cell_walls.BOTTOM,True)
            else:
                self._cells[col1][row1].break_wall(cell_walls.TOP,True)
                self._cells[col1][row2].break_wall(cell_walls.BOTTOM,True)
        
        # redraw both cells
        self._draw_cell(col1, row1)
        self._draw_cell(col2, row2)

    def _reset_visited(self):
        for col in self._cells:
            for cell in col:
                cell.unvisit()

    def _cells_are_pathable(self, col1, row1, col2, row2):
        # Check if the two cells are adjacent
        if abs(col1 - col2) + abs(row1 - row2) != 1:
            return False    
        # Check if the two cells are the same
        if col1 == col2 and row1 == row2:
            return False
        # Check if the two cells are in the same row
        if row1 == row2:
            #They are! So we check if the two cells are adjacent horizontally
            if col1 < col2:
                cell1_wall = cell_walls.RIGHT
                cell2_wall = cell_walls.LEFT
            else:
                cell1_wall = cell_walls.LEFT
                cell2_wall = cell_walls.RIGHT
        else:
            #They are not! So we check if the two cells are adjacent vertically
            if row1 < row2:
                cell1_wall = cell_walls.BOTTOM
                cell2_wall = cell_walls.TOP
            else:
                cell1_wall = cell_walls.TOP
                cell2_wall = cell_walls.BOTTOM
            # Check if the walls between the two cells are broken
        cell1_has_wall = self._cells[col1][row1].is_wall_broken(cell1_wall) 
        cell2_has_wall = self._cells[col2][row2].is_wall_broken(cell2_wall)
        print(f"cell 1 {cell1_has_wall}; cell 2 {cell2_has_wall}")
        if cell1_has_wall and cell2_has_wall:
            #print("Pathable")
            return True
        return False

    def solve(self):
        return self._solve_r(0,0)
    
    def _solve_r(self,col,row):
        print(f"Starting on cell {col},{row}")
        self._animate()
        self._cells[col][row].visit()
        if row == self.num_rows -1 and col == self.num_cols -1:
            print("Found the end!")
            return True
        to_visit = []
        # check our four directions
        if col > 0 and not self._cells[col - 1][row]._visited:
            to_visit.append((col - 1, row))
            
        if col < (self.num_cols - 1) and not self._cells[col + 1][row]._visited:
            to_visit.append((col + 1, row))
        
        if row > 0 and not self._cells[col][row-1]._visited:
            to_visit.append((col, row - 1))
        
        if row < (self.num_rows - 1) and not self._cells[col][row+1]._visited:
            to_visit.append((col, row + 1))

        for cell_loc in to_visit:
            cell = self._cells[cell_loc[0]][cell_loc[1]]
            if not cell._visited and self._cells_are_pathable(col,row,cell_loc[0],cell_loc[1]):
                print(f"okay to move from {col},{row} to {cell_loc[0]},{cell_loc[1]}")
                self._cells[col][row].draw_move(cell)
                if self._solve_r(cell_loc[0],cell_loc[1]):
                    return True
                else:
                    self._cells[col][row].draw_move(cell,True)
                
        return False