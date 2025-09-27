simulating = False
failed = False

# Simulation config
movement_type = 'Cardinal'
sx, sy = None, None
gx, gy = None, None
level_name = ''
heuristic = 'Diagonal Manhattan'
heuristic_weight = 1
paused = False
delay = 1
speed = 'Normal'

# Editor config
draw_type = 'wall'
editor_has_start = False
editor_has_goal = False

def set_editor_type(tile_type):
    """
    Sets what tile to draw with.

    Parameters:
        type (str): 'empty', 'wall', 'start', or 'goal'.
    """
    global draw_type
    draw_type = tile_type

def set_movement_type(moveset):
    """
    Sets movement_type.
    
    Parameters:
        moveset (str): 'Cardinal' or 'Diagonal'
    """
    global movement_type
    movement_type = moveset

def get_moves(moveset):
    """
    Returns list of moves based on moveset
    
    Parameters:
        moveset (str): Moveset to be used (Cardinal or Diagonal).
    
    Returns:
        list[list[int]]: List of moves belonging to moveset.
    """
    if moveset == 'Cardinal':
        return [[0,-1], [-1,0], [1,0], [0,1]]
    else:
        return [[-1,-1], [0,-1], [1,-1],
                [-1, 0],         [1, 0],
                [-1, 1], [0, 1], [1, 1]]

def get_move_cost(move) -> int:
    """
    Returns cost of move based on what type of move it is.

    Returns:
        int: cost of the move. 100 for Cardinal, 141 for Diagonal.
    """
    cardinal_moves = {(0,-1), (-1,0), (1,0), (0,1)}
    if tuple(move) in cardinal_moves:
        return 100
    else:
        return 141

def is_valid_pos(x, y, move, grid):
    """
    Checks whether an move results in a valid position.

    Parameters:
        x, y          (int): Position coordinates.
        move    (list[int]): Move to apply.
        grid               : Grid object to check if position is valid.
    
    Returns:
        bool: True if valid position, False if invalid position.
    """
    nx = x + move[0]
    ny = y + move[1]
    if grid.is_OOB(nx, ny):
        return False
    diag_valid = diagonal_check(x, y, move, grid)
    state = grid.get(nx, ny)
    return state in ['empty', 'goal'] and diag_valid

def diagonal_check(x, y, move, grid):
    """
    Checks neighboring tiles to disallow jumping over corners.
    
    Parameters:
        x, y          (int): Position coordinates.
        move    (list[int]): Diagonal move to apply.
        grid               : Grid object to check if diagonal movement is valid.

    Returns:
        bool: True if diagonal move doesn't jump over a corner, False if it does.
    """
    dx, dy = move
    if abs(dx) == 1 and abs(dy) == 1:
        if grid.get(x + dx, y) == "wall": 
            return False
        if grid.get(x, y + dy) == "wall":
            return False
    return True