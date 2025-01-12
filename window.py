import sys
from constants import *
from tkinter import Tk, BOTH, Canvas, Button, Entry, Grid, StringVar
import time
import random



class Window():
    def __init__(self, width, height):
        self.__root = Tk()
        self.__root.title("KazaNet Maze Solver")
        self.__root.geometry(f"{width}x{height}")
        self.__running = False
        self.__canvas = Canvas(self.__root, width=width, height=height, bg="black")
        self.__canvas.pack(fill=BOTH, expand=True)
        self.__root.protocol("WM_DELETE_WINDOW", self.close)
        self.x_entry = StringVar()
        self.y_entry = StringVar()
        

    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()

    def create_buttons(self, generate, solve):
        button = Button(self.__root, 
                   text="Generate Maze", 
                   command=generate,
                   activebackground="blue", 
                   activeforeground="white",
                   anchor="center",
                   bd=3,
                   bg="lightgray",
                   cursor="hand2",
                   disabledforeground="gray",
                   fg="black",
                   font=("Arial", 12),
                   height=2,
                   highlightbackground="black",
                   highlightcolor="green",
                   highlightthickness=2,
                   justify="center",
                   overrelief="raised",
                   padx=10,
                   pady=5,
                   width=15,
                   wraplength=100)

        button.pack(padx=20, pady=20)
        button.place(x=50,y=50)

        button2 = Button(self.__root, 
                   text="Solve Maze", 
                   command=solve,
                   activebackground="blue", 
                   activeforeground="white",
                   anchor="center",
                   bd=3,
                   bg="lightgray",
                   cursor="hand2",
                   disabledforeground="gray",
                   fg="black",
                   font=("Arial", 12),
                   height=2,
                   highlightbackground="black",
                   highlightcolor="green",
                   highlightthickness=2,
                   justify="center",
                   overrelief="raised",
                   padx=10,
                   pady=5,
                   width=15,
                   wraplength=100)

        button2.pack(padx=20, pady=20)
        button2.place(x=50,y=200)

        x_entry = Entry(self.__root,textvariable = self.x_entry, font=('calibre',10,'normal'), width=5)
        y_entry = Entry(self.__root,textvariable = self.y_entry, font=('calibre',10,'normal'), width=5)

        x_entry.place(x=50,y=125)
        y_entry.place(x=125,y=125)
        # passw_label.grid(row=1,column=0)
        # passw_entry.grid(row=1,column=1)
        #button.grid(row=1,column=1)
        #button2.grid(row=2,column=1)

    def wait_for_close(self):
        self.__running = True
        while self.__running:
            self.redraw()

    def close(self):
        self.__running = False

    def draw_line(self, line: 'Line', fill_colour: str, tag = "lines"):
        return line.draw(self.__canvas,fill_colour, tag)
    
    def delete_lines(self,tag = "lines"):
        self.__canvas.delete(tag)
    
    def canvas_delete(self,id):
       self.__canvas.delete(id)

class Cell():
    def __init__(self, x, y, size = CELL_SIZE, window: Window = None, colour = "white"):
        self.coords = [Point(x,y),Point(x+size,y)
                       ,Point(x+size,y+size),Point(x,y+size)]
        self.__window = window
        self.size = size
        self.colour = colour
        # status for walls, in order top, right, bottom, left
        self.has_walls = [True,True,True,True]
        self.walls = [Line(self.coords[0],self.coords[1]),
                      Line(self.coords[1],self.coords[2]),
                      Line(self.coords[2],self.coords[3]),
                      Line(self.coords[3],self.coords[0])]
        self._wall_lines = [None for i in range(4)]
        self.center = Point(x+(self.size//2),y+(self.size//2))
        self._visited = False
        self.correct_path = False

    def draw_move(self, to_cell, undo=False):
        if self.__window == None:
            return
        fill_colour = "gray" if undo else "red"
        self.__window.draw_line(Line(self.center,to_cell.center),fill_colour,"solve")
        self.correct_path = not undo
    
    def draw(self):
        if self.__window == None:
            return
        for i in range(len(self.has_walls)):
            if self.has_walls[i] and self._wall_lines[i] is None:

                self._wall_lines[i] = self.__window.draw_line(self.walls[i],self.colour)
    
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
    
    def draw(self, canvas: Canvas, fill_colour, tag="lines"):
        return canvas.create_line(self.coords[0][0], self.coords[0][1], 
                           self.coords[1][0], self.coords[1][1],
                           fill=fill_colour, width=self.width,tags=tag)
        

class Maze():
    def __init__(
        self,
        x,
        y,
        num_rows,
        num_cols,
        settings,
        win = None,
        seed = None,
    ):
        self.x = x
        self.y = y
        self.num_rows = num_rows
        self.num_cols = num_cols
        
        self._win = win
        self.settings = settings
        if seed:
            self.seed = random.seed(seed)
        else:
            self.seed = 0
        
        # calculate cell_size to fit allocated space in our window using the settings

        self.__calc_cell_size()

        self._cells = []
        self.__generating = False
    
    def __calc_cell_size(self):
        avail_x = self.settings.window_width - self.settings.left_indent - self.settings.right_indent
        avail_y = self.settings.window_height - self.settings.top_indent - self.settings.bottom_indent
        self.cell_size = min(avail_x // self.num_cols, avail_y // self.num_rows)

    def reset_maze(self):
        
        self._win.delete_lines()
        self._win.delete_lines("solve")
        self._cells = []


    def generate_maze(self):
        if self.__generating:
            return
        # lets just force a reset to be safe for now
        self.reset_maze()
        self.__generating = True
        x_var = 0
        y_var = 0
        if self._win is not None and self._win.x_entry is not None and self._win.y_entry is not None:
            try:
                x_var = int(self._win.x_entry.get())
                y_var = int(self._win.y_entry.get())
            except ValueError:
                print("Invalid input for x or y")
            
            if x_var > 0 and y_var > 0:
                self.num_rows = min(y_var,200)
                self.num_cols = min(x_var,200)
                self.__calc_cell_size()
        
        self._create_cells()

        self._break_entrance_and_exit()
        sys.setrecursionlimit(20+(self.num_cols*self.num_rows))
        self._break_walls_r(0,0)
        sys.setrecursionlimit(1000)
        self._reset_visited()
        self.__generating = False



    def _create_cells(self):
        
        x = self.x
        
        for col in range(self.num_cols):
            col_list = []
            self._cells.append(col_list)
            y = self.y
            for row in range(self.num_rows):
                col_list.append(Cell(x,y,self.cell_size, self._win,"white"))
                y += self.cell_size
                
                #self._draw_cell(col,row)
            x += self.cell_size
            
            
        
    def _draw_cell(self,col, row):
        if self._win == None:
            return
        self._cells[col][row].draw()
        
        self._animate(0.01)
        
    
    def _animate(self,timer=0.05,override=False):
        if self._win == None:
            return
        self._win.redraw()
        if self.num_cols * self.num_rows > 150 and not override:
            #don't animate! too many cells, unless ovveride was given (eg, solve drawing)
            return
        time.sleep(timer)

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
        #print(f"cell 1 {cell1_has_wall}; cell 2 {cell2_has_wall}")
        if cell1_has_wall and cell2_has_wall:
            #print("Pathable")
            return True
        return False

    def solve(self):
        # reset solve in case we are trying again.  This in prep for having multipe solve options (eg, directional preference)
        self._reset_visited()
        self._win.delete_lines("solve")
        sys.setrecursionlimit(20+(self.num_cols*self.num_rows))
        result = self._solve_r(0,0)
        sys.setrecursionlimit(1000)
        moves = 0
        correct_path = 1 # start at 1 to include origin.
        for col in self._cells:
            for c in col:
                if c._visited:      
                    moves += 1
                if c.correct_path:
                    correct_path += 1

        print(f"Moves: {moves} ({(moves / (self.num_cols * self.num_rows) * 100)}%). Solve path length: {correct_path}. Delta: {moves - correct_path}")
        print(f"Efficiency Score: {correct_path/moves*100}%")
        return result
        
    
    def _solve_r(self,col,row):
        self._animate(0.01,True)
        self._cells[col][row].visit()
        if row == self.num_rows -1 and col == self.num_cols -1:
            return True
        to_visit = []
        # check our four directions. Prefer east and south to try and tend towards that corner.
        if col < (self.num_cols - 1) and not self._cells[col + 1][row]._visited:
            to_visit.append((col + 1, row))
        
        if row < (self.num_rows - 1) and not self._cells[col][row+1]._visited:
            to_visit.append((col, row + 1))

        if col > 0 and not self._cells[col - 1][row]._visited:
            to_visit.append((col - 1, row))
            
        if row > 0 and not self._cells[col][row-1]._visited:
            to_visit.append((col, row - 1))
        
        

        for cell_loc in to_visit:
            cell = self._cells[cell_loc[0]][cell_loc[1]]
            if not cell._visited and self._cells_are_pathable(col,row,cell_loc[0],cell_loc[1]):
                #print(f"okay to move from {col},{row} to {cell_loc[0]},{cell_loc[1]}")
                self._cells[col][row].draw_move(cell)
                if self._solve_r(cell_loc[0],cell_loc[1]):
                    return True
                else:
                    self._cells[col][row].draw_move(cell,True)
                
        return False
    
