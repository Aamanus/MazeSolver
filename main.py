from window import *
from constants import *

def main():
    settings = Settings()
    win = Window(settings.window_width, settings.window_height)
    maze = Maze(settings.left_indent,settings.right_indent,25,25,settings,win)
    win.create_buttons(maze.generate_maze, maze.solve)
    win.wait_for_close()


if __name__ == "__main__":
    main()