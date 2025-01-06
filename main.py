from window import *
from constants import *

def main():
    win = Window(800, 600)
    maze = Maze(CELL_SIZE,CELL_SIZE,10,10,CELL_SIZE,win)
    maze.solve()

    win.wait_for_close()

if __name__ == "__main__":
    main()