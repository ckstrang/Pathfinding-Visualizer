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

def set_editor_type(type):
    """
    Sets what tile to draw with.

    Parameters:
        type (str): 'empty', 'wall', 'start', or 'goal'.
    """
    global draw_type
    draw_type = type

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
        moveset (str): Moveset to be used (cardinal or diagonal).
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
    - Cardinal (straight) moves: cost of 100
    - Diagonal moves: cost of 141
    Returns:
        int: cost of move
    """
    if move in [[0,-1], [-1,0], [1,0], [0,1]]:
        return 100
    else:
        return 141

def is_valid_pos(x, y, move, grid):
    """
    Checks whether an move results in a valid position.
    
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
    
    Returns:
        legal (bool): True if diagonal move doesn't jump over a corner, False if it does.
    """
    legal = True
    if move == [-1, -1]:
        # check left
        if grid.get(x-1, y) == 'wall': legal = False
        #check up
        if grid.get(x, y-1) == 'wall': legal = False
    elif move == [1, -1]:
        # check right
        if grid.get(x+1, y) == 'wall': legal = False
        # check up
        if grid.get(x, y-1) == 'wall': legal = False
    elif move == [-1, 1]:
        # check left
        if grid.get(x-1, y) == 'wall': legal = False
        # check down
        if grid.get(x, y+1) == 'wall': legal = False
    elif move == [1, 1]:
        # check right
        if grid.get(x+1, y) == 'wall': legal = False
        # check down
        if grid.get(x, y+1) == 'wall': legal = False
    return legal