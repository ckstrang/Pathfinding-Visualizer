import json
import os
from tkinter import messagebox

from customtkinter import CTkInputDialog, filedialog

import Algorithms.A_Star as A_Star
import Algorithms.BFSDFS as BFSDFS
import Core.config as config
from UI.grid import Grid

# Delay is the delay (ms) in performing search steps.
SPEED_TO_DELAY = {
    'Very Fast': 1,
    'Fast': 1,
    'Normal': 20,
    'Slow': 100,
    'Very Slow': 200,
}

# Step rate is how often the GUI updates and shows search progress.
# 1 means every frame
# 3 means every 3 frames
# 30 means every 30 frames
SPEED_TO_STEP_RATE = {
    'Very Fast': 30,
    'Fast': 3,
    'Normal': 1,
    'Slow': 1,
    'Very Slow': 1,
}

def draw(event, GUI):
    """
    Draw on grid when mouse clicked.
    
    Parameters:
        GUI: Reference to the main GUI containing canvas and grid.
    """
    
    # Block adjusting start and goal while simulating
    if config.draw_type in ['start', 'goal'] and config.simulating:
        return
    
    # Block placing more than one start position
    if config.draw_type == 'start' and config.editor_has_start:
        config.draw_type = 'wall'
    
    # Block placing more than one goal position
    if config.draw_type == 'goal' and config.editor_has_goal:
        config.draw_type = 'wall'
    
    canvas = GUI.canvas
    grid = GUI.grid

    # Calculate grid coord based on event coordinates
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    grid_width = grid.cols * grid.tile_size
    grid_height = grid.rows * grid.tile_size
    offset_x = (canvas_width - grid_width) // 2
    offset_y = (canvas_height - grid_height) // 2

    x = (event.x - offset_x) // grid.tile_size
    y = (event.y - offset_y) // grid.tile_size

    try:
        state = grid.grid[y][x].state
    except IndexError:
        return
    
    # Block placing a wall on the starting position
    if state == 'start' and config.draw_type == 'wall':
        return
    
    # Block placing a wall on the goal position
    if state == 'goal' and config.draw_type == 'wall':
        return
    
    if config.draw_type in ['start', 'goal']:
        grid.set_obj(x, y)
        grid.draw()

    grid.update_tile(x, y, config.draw_type)
    canvas.update_idletasks()

def erase(event, GUI):
    """
    Erase on grid when mouse clicked.

    Parameters:
        GUI: Reference to the main GUI containing canvas and grid.
    """
    canvas = GUI.canvas
    grid = GUI.grid

    # Calculate grid coord based on event coordinates
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()

    grid_width = grid.cols * grid.tile_size
    grid_height = grid.rows * grid.tile_size

    offset_x = (canvas_width - grid_width) // 2
    offset_y = (canvas_height - grid_height) // 2

    x = (event.x - offset_x) // grid.tile_size
    y = (event.y - offset_y) // grid.tile_size

    if config.draw_type in ['start', 'goal']:
        grid.clear_obj(x, y)
        grid.draw()
        
    grid.update_tile(x, y, 'empty')
    canvas.update_idletasks()

def run_algorithm(algo: str, grid: Grid, GUI, speed, heuristic: str, weight):
    """
    Runs the selected pathfinding algorithm in a step based simulation.

    Parameters:
        algo (str)          : Algorithm name (BFS, DFS, A*, UCS, GBeFS).
        grid (Grid)         : Grid object where the simulation runs.
        GUI                 : Reference to the main GUI containing canvas and grid.
        speed (str)         : Speed selection (Very Fast, Fast, Normal, Slow, Very Slow)
        heuristic (str)     : Heuristic type for A* (Manhattan, Diagonal, None)
        weight (float | str): Heuristic weight (0, 0.5, 1, 2, Infinity)
    """
    def update():
        """Update GUI"""
        grid.show_open(search.get_frontier())
        grid.show_closed(search.get_visited())
        route = search.get_route()
        if route and not config.simulating:
                grid.visualize_route(route, GUI, 1)
        GUI.canvas.update_idletasks()

    def simulation_step():
        """Perform single search step"""
        global steps

        if not config.simulating:
            update()
            return

        if not config.paused:
            steps += 1
            if steps % SPEED_TO_STEP_RATE.get(config.speed, 10) == 0:
                update()
            if not search.step():
                config.simulating = False
                if config.failed:
                    messagebox.showinfo(title='Search failed to find a path.', message='The search has completed and failed to find a path.')
                update()
                return

        GUI.after(SPEED_TO_DELAY.get(config.speed, 50), simulation_step)

    _clear_sim_results(grid)
    grid.draw()


    canvas_width = GUI.canvas.winfo_width()
    canvas_height = GUI.canvas.winfo_height()
    grid.tile_size = min(canvas_width // grid.cols, canvas_height // grid.rows)
    grid.draw()

    if algo == 'GBeFS' or weight == 'Infinity':
        weight = 100000
    if algo == 'UCS':
        weight = 1
        heuristic = 'None'
    weight = float(weight)

    sx, sy = grid.get_start()
    gx, gy = grid.get_goal()

    if sx == -1 or gx == -1:
        messagebox.showerror(title='Failed to run search', message='Invalid Start or Goal position.')
        return

    global search
    if algo in ['A*', 'GBeFS', 'UCS']:
        search = A_Star.Pathfinder(grid, sx, sy, gx, gy, heuristic, weight)
    else:
        search = BFSDFS.Pathfinder(grid, sx, sy, gx, gy, algo)

    global steps
    steps = 0

    config.simulating = True
    config.paused = False

    config.delay = SPEED_TO_DELAY.get(speed, 50)
    speed = SPEED_TO_STEP_RATE.get(speed, 10)
    simulation_step()

def _clear_sim_results(grid):
    """
    Clears any previous simulation visualization (open list, closed list, and route), and resets config.failed to False.
    """
    config.failed = False
    for row in grid.grid:
        for tile in row:
            if tile.state in ('open', 'closed', 'route'):
                tile.state = 'empty'


def clear_grid(grid):
    """
    Clears the grid based on if a simulation visualization is present.
    If a simulation is present, this will clear the visualization.
    If no simulation is present, this will clear the grid.

    Parameters:
        grid (Grid): Grid to modify.
    
    """
    if grid.sim_present:
        _clear_sim_results(grid)
        grid.sim_present = False
    else:
        grid.reset()
    grid.draw()

def save_level(GUI):
    """
    Saves the grid as a .JSON file to a user specified route.
    
    Parameters:
        GUI: Reference to the main GUI containing canvas and grid.
    """
    if not config.editor_has_start or not config.editor_has_goal:
        messagebox.showerror(title='File failed to save', message='Missing Start or Goal position.')
        return
    dialog = CTkInputDialog(title="Save Level", text="Enter a filename:")
    file_name = dialog.get_input()

    if not file_name:
        return
    if not file_name.endswith('.json'):
        file_name += '.json'

    current_dir = os.path.dirname(os.path.abspath(__file__))
    level_dir = os.path.abspath(os.path.join(current_dir, '..', 'Assets', 'Levels'))
    level_path = os.path.join(level_dir, file_name)

    if GUI.grid.sim_present:
        _clear_sim_results(GUI.grid)
        GUI.grid.sim_present = False

    _save_grid(GUI.grid, file_name=level_path)
    GUI.retrieve_levels()

def _save_grid(grid, file_name='level.json'):
    """Writes the grid into a .JSON.
    
    Encoding:
        0 = empty,
        1 = wall,
        2 = start,
        3 = goal,
    
    Parameters:
        grid     (Grid): Grid to write.
        file_name (str): File name.
    """
    save_map = {
        'empty': 0,
        'wall' : 1,
        'start': 2,
        'goal' : 3 
    }
    serialized_grid = []
    for row in grid.grid:
        serialized_row = []
        for node in row:
            serialized_row.append(save_map[node.state])
        serialized_grid.append(serialized_row)
    with open(file_name, 'w') as f:
        json.dump(serialized_grid, f)

def load_level(GUI, file_name):
    """
    Loads level from .JSON file.
    
    Parameters:
        GUI            : Reference to the main GUI containing canvas and grid.
        file_name (str): File name.
    """
    config.level_name = file_name

    current_dir = os.path.dirname(os.path.abspath(__file__))
    level_dir = os.path.abspath(os.path.join(current_dir, '..', 'Assets', 'Levels'))
    level_path = os.path.join(level_dir, file_name)

    with open(level_path, 'r') as f:
        serialized_grid = json.load(f)

    rows = len(serialized_grid)
    cols = len(serialized_grid[0])

    GUI.update_idletasks()
    canvas_width = GUI.canvas.winfo_width()
    canvas_height = GUI.canvas.winfo_height()

    # Calculate cell size 
    cell_size_w = canvas_width // cols
    cell_size_h = canvas_height // rows
    cell_size = min(cell_size_w, cell_size_h)


    GUI.grid = Grid(rows=rows, cols=cols, canvas=GUI.canvas, cell_size=cell_size)

    _apply_grid_data(GUI.grid, serialized_grid)

    config.editor_has_goal = True
    config.editor_has_start = True
    GUI.grid.draw()

def _apply_grid_data(grid, serialized_grid):
    """
    Applies grid data to the existing GUI grid.

    Parameters:
        grid    (Grid) : Grid to write.
        serialized_grid: Grid as read in by load_level().
    """
    load_map = {
        0: 'empty',
        1: 'wall',
        2: 'start',
        3: 'goal'
    }

    for row_index in range(len(serialized_grid)):
        for col_index in range(len(serialized_grid[row_index])):
            value = serialized_grid[row_index][col_index]
            state = load_map.get(value, "empty")

            grid.grid[row_index][col_index].state = state

            if state == "start":
                grid.sx, grid.sy = col_index, row_index
            elif state == "goal":
                grid.gx, grid.gy = col_index, row_index

def algo_selection(GUI, algo):
    """
    Enables the GUI dropdown for algorithm selection.

    Parameters:
        GUI        : Reference to the main GUI containing canvas and grid.
        algo (str) : Algorithm name (BFS, DFS, A*, UCS, GBeFS).
    """
    GUI.toggle_weight_option(algo)

def size_select(GUI, size):
    """
    Handles grid size selection.
    Redraws the grid based on size selection.
    
    Parameters:
        GUI: Contains the grid to be redrawn.
        size (str): Grid dimensions.
    """
    size = int(size.split('x')[0])
    
    GUI.update_idletasks()
    canvas_width = GUI.canvas.winfo_width()
    canvas_height = GUI.canvas.winfo_height()

    # Calculate cell size
    cell_size_w = canvas_width // size
    cell_size_h = canvas_height // size
    GUI.cell_size = min(cell_size_w, cell_size_h)

    GUI.grid = Grid(rows=size, cols = size, canvas=GUI.canvas, cell_size=GUI.cell_size)
    GUI.grid.draw()

    config.editor_has_start = False
    config.editor_has_goal = False

def toggle_pause():
    """Pauses and unpauses the simulation."""
    config.paused = not config.paused

def set_speed(speed):
    """
    Sets simulation speed
    
    Parameters:
        speed (str) : Speed selection (Very Fast, Fast, Normal, Slow, Very Slow)
    """
    config.speed = speed
