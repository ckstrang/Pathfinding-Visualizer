import Core.config as config
import os
import customtkinter as ctk
from PIL import Image, ImageTk
import time

TILE_COLORS = {
    'empty': 'white',
    'wall': 'black',
    'start': 'orange',
    'goal': 'purple',
    'open': 'green',
    'closed': 'red',
    'route': 'blue'
}

class Node:
    """
    Represents a single tile or cell in the grid.

    Attributes:
        x, y (int, int): Coordinates of the node.
        size (int): Size of node in pixels.
        state (str): The current state of the tile ('empty', 'wall', etc. See TILE_COLORS for all possible states).
        parent (Node | None): Reference to parent node along route.
        move (list[int, int] | None): Move taken to reach node from parent.
        canvas_id (int | None): Canvas rectangle ID for rendering.
    """
    def __init__(self, x, y, size, parent, move):
        self.x = x
        self.y = y
        self.size = size
        self.state = 'empty'
        self.parent = parent
        self.move = move

    def get_coords(self, grid):
        """
        Returns screen coordinates of the tile on the canvas.

        Returns:
            tuple[int, int, int, int]: Corner coordinates of node.
        """
        grid_width = grid.cols * grid.tile_size
        grid_height = grid.rows * grid.tile_size

        canvas_width = grid.canvas.winfo_width()
        canvas_height = grid.canvas.winfo_height()

        offset_x = (canvas_width - grid_width) // 2
        offset_y = (canvas_height - grid_height) // 2

        x1 = self.x * grid.tile_size + offset_x
        y1 = self.y * grid.tile_size + offset_y
        x2 = x1 + grid.tile_size
        y2 = y1 + grid.tile_size
        return x1, y1, x2, y2

class Grid:
    """
    Represents the 2D grid environment for pathfinding and rendering.

    Attributes:
        rows (int): Number of rows in the grid.
        cols (int): Number of columns in the grid.
        canvas (tk.Canvas): Canvas used to draw the grid.
        tile_size (int): Size of each tile in pixels.
        grid (list[list[Node]]): 2D list of Node objects.
        sx, sy (int): Coordinates of the start node.
        gx, gy (int): Coordinates of the goal node.
        sim_present (bool): Whether a simulation is currently visualized.
    """
    def __init__(self, rows: int, cols: int, canvas: ctk.CTkCanvas, cell_size: int):
        """
        Initializes the grid and binds to the canvas resize event.

        Parameters:
            rows (int): Number of rows in the grid.
            cols (int): Number of columns in the grid.
            canvas (tk.Canvas): The canvas to draw on.
            cell_size (int): Pixel size of each cell.
        """
        self.rows = rows
        self.cols = cols
        self.canvas = canvas
        self.tile_size = cell_size
        self.grid = []
        self.sx, self.sy = -1, -1
        self.gx, self.gy = -1, -1
        self.route = []
        self.sim_present = False
        self.image_refs = {}
        self.route_image_refs = {}
        self.init_images()
        self.init_grid()

    def init_images(self):
        self.image_refs = {
            'goal': self.get_element_icon('Goal.png', self.tile_size),
            'start': self.get_element_icon('Start.png', self.tile_size)
        }
        self.route_image_refs = {
            '[0, 1]': self.get_element_icon('Down.png', self.tile_size),
            '[0, -1]': self.get_element_icon('Up.png', self.tile_size),
            '[1, 0]': self.get_element_icon('Right.png', self.tile_size),
            '[-1, 0]': self.get_element_icon('Left.png', self.tile_size),

            '[1, 1]': self.get_element_icon('DownRight.png', self.tile_size),
            '[1, -1]': self.get_element_icon('UpRight.png', self.tile_size),
            '[-1, 1]': self.get_element_icon('DownLeft.png', self.tile_size),
            '[-1, -1]': self.get_element_icon('UpLeft.png', self.tile_size)
        }

    def init_grid(self):
        """Initializes the 2D grid with empty Node objects."""
        for y in range(self.rows):
            row = []
            for x in range(self.cols):
                row.append(Node(x, y, self.tile_size, None, None))
            self.grid.append(row)

    def draw(self):
        """Clears and redraws the entire grid on the canvas."""
        self.canvas.delete('all')

        grid_width = self.cols * self.tile_size
        grid_height = self.rows * self.tile_size

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        offset_x = (canvas_width - grid_width) // 2
        offset_y = (canvas_height - grid_height) // 2

        for row in self.grid:
            for node in row:
                x1 = node.x * self.tile_size + offset_x
                y1 = node.y * self.tile_size + offset_y
                x2 = x1 + self.tile_size
                y2 = y1 + self.tile_size

                rect_id = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=TILE_COLORS[node.state],
                    outline='gray'
                )
                if node.state == 'goal':
                    image = self.image_refs['goal']
                    self.canvas.create_image(x1, y1, image=image, anchor='nw')
                if node.state == 'start':
                    image = self.image_refs['start']
                    self.canvas.create_image(x1, y1, image=image, anchor='nw')
                node.canvas_id = rect_id

    def set_obj(self, x: int, y: int):
        """
        Sets an objective (start or goal) at a given pixel location. 
        Reads config.draw_type for the objective type.

        Parameters:
            x, y (int, int): coordinates.
        """
        if not self.is_OOB(x, y):
            node = self.grid[y][x]
            if node.state == 'start' or node.state == 'goal':
                return
            if config.editor_has_start and config.draw_type == 'start':
                return
            if config.editor_has_goal and config.draw_type == 'goal':
                return
            node.state = config.draw_type
            if config.draw_type == 'start':
                config.editor_has_start = True
                self.sx, self.sy = x, y
            elif config.draw_type == 'goal':
                config.editor_has_goal = True
                self.gx, self.gy = x, y

    def clear_obj(self, x: int, y: int):
        """
        Clears an objective (start or goal) at the given pixel location, resetting the state to 'empty'.

        Paramaters:
            px, py (int, int): coordinates in pixels.
        """
        if not self.is_OOB(x, y):
            node = self.grid[y][x]
            if node.state == 'start':
                config.editor_has_start = False
                self.sx, self.sy = -1, -1
            if node.state == 'goal':
                config.editor_has_goal = False
                self.gx, self.gy = -1, -1
            node.state = 'empty'


    def is_OOB(self, x: int, y: int):
        """
        Checks if the given tile coordinates are out of bounds.

        Paramaters:
            x, y (int, int): Tile coordinates.

        Returns:
            bool: True if out of bounds, False otherwise.
        """
        return not (0 <= x < self.cols and 0 <= y < self.rows)

    def get(self, x: int, y: int):
        """
        Gets the state of the tile at the given coordinates.

        Paramaters:
            x, y (int, int): Tile coordinates.

        Returns:
            str: The tile state (e.g., 'wall', 'empty').
        """
        if self.is_OOB(x, y):
            return 'wall'
        return self.grid[y][x].state

    def reset(self):
        """
        Resets the entire grid and simulation state to default.
        """
        for row in self.grid:
            for node in row:
                node.state = 'empty'
        config.editor_has_start = False
        config.editor_has_goal = False
        self.sx, self.sy = -1, -1
        self.gx, self.gy = -1, -1
        self.open = []
        self.closed = []
        self.route = []

    def get_start(self):
        """
        Returns:
            list[int, int]: The [x, y] coordinates of the start tile.
        """
        return [self.sx, self.sy]

    def get_goal(self):
        """
        Returns:
            list[int, int]: The [x, y] coordinates of the goal tile.
        """
        return [self.gx, self.gy]

    def show_open(self, open_list):
        """
        Updates the grid to display the current open list.

        Parameters:
            open_list (list[tuple[int, int]]): Coordinates of open tiles.
        """
        for x, y in open_list:
            if (x, y) in [(self.sx, self.sy), (self.gx, self.gy)]:
                continue
            self.grid[y][x].state = 'open'
            self.update_tile(x, y, 'open')
        self.sim_present = True

    def show_closed(self, closed_list: list[tuple[int, int]]):
        """
        Updates the grid to display the current closed list.

        Parameters:
            closed_list (list[tuple[int, int]]): Coordinates of closed tiles.
        """
        for x, y in closed_list:
            if (x, y) in [(self.sx, self.sy), (self.gx, self.gy)]:
                continue
            self.grid[y][x].state = 'closed'
            self.update_tile(x, y, 'closed')
        self.sim_present = True

    def visualize_route(self, route, GUI, index: int):
        """
        Visualizes the route, from goal backwards to the start.

        Parameters:
            route (list[Node]): List of Node objects in the final route.
            GUI          (GUI): Reference to the GUI for displaying backtracking.
            index        (int): Index into the route.
        """
        if index >= len(route) - 1:
            return
        node = route[index]
        if not node.move:
            return
        if self.grid[node.y][node.x].state in ['start', 'goal']:
            GUI.after(55, lambda: self.visualize_route(route, GUI, index + 1))
        if (node.x, node.y) in [(self.sx, self.sy), (self.gx, self.gy)]:
            GUI.after(55, lambda: self.visualize_route(route, GUI, index + 1))
        self.grid[node.y][node.x].state = 'route'
        self.grid[node.y][node.x].parent = node.parent
        self.grid[node.y][node.x].move = node.move
        self.update_tile(node.x, node.y, 'route')
        GUI.after(55, lambda: self.visualize_route(route, GUI, index + 1))

    def update_tile(self, x: int, y: int, state: str) -> None:
        """
        Updates the fill color of a single tile on the canvas.

        Parameters:
            x, y (int, int): Tile coordinates.
            state     (str): New tile state ('open', 'closed', 'route', etc.).
        """
        tile = self.grid[y][x]
        if tile.state == 'start' or tile.state == 'goal':
            return
        tile.state = state
        if tile.canvas_id is not None:
            if tile.state == 'route':
                    x1, y1, x2, y2 = tile.get_coords(self)
                    image = self.route_image_refs[str(tile.move)]
                    self.canvas.create_image(x1, y1, image=image, anchor='nw')
            self.canvas.itemconfig(tile.canvas_id, fill=TILE_COLORS[state])


    def get_element_icon(self, name: str, size: int=16):
        """
        Helper function to get icons for UI elements.

        Parameters:
            name (str): Name of the icon PNG file.
            size (int): Size of the icon in pixels (width and height).

        Returns:
            PhotoImage: The requested icon in the specified size.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.abspath(os.path.join(base_dir, '..', 'assets', 'icons', name))

        img = Image.open(icon_path).resize((size, size))
        return ImageTk.PhotoImage(img)
