import Core.config as config
from collections import deque

class Node:
    """
    Represents a node in the search space.

    Attributes:
        x, y      (int, int): Coordinates of the node.
        parent        (node): Parent node from which this node was reached.
        move (list[int,int]): The move taken to reach this node.
    """
    def __init__(self, x, y, parent, move):
        self.x = x
        self.y = y
        self.parent = parent
        self.move = move

class Pathfinder:
    """
    Implements a pathfinding search algorithm (BFS or DFS) on a 2D grid.

    Attributes:
        grid          (list[list[str]]): The 2D grid representing the environment.
        start                (int, int): Starting coordinates of the search agent.
        goal                 (int, int): Goal coordinates.
        mode                      (str): The search algorithm (BFS or DFS)
        moves    (list[list[int, int]]): List of movement directions (cardinal or diagonal).
        route              (list[Node]): List of nodes representing the solution route.
        frontier         (deque | list): The list of nodes to be explored.
        visited  (set[tuple[int, int]]): Set of visited node coordinates.
        enqueued (set[tuple[int, int]]): Set of coordinates currently in the frontier.
    
    """
    def __init__(self, grid, sx, sy, gx, gy, mode: str):
        """
        Initializes the Search object and begins the simulation.

        Args:
            grid (list[list[str]]): The grid environment.
            sx, sy      (int, int): Starting coordinates of the search agent.
            gx, gy      (int, int): Goal coordinates.
            mode             (str): The algorithm mode ('BFS' or 'DFS').
        """
        self.grid = grid
        self.moves = config.get_moves(config.movement_type)
        self.enqueued = set()
        self.mode = mode

        self.start = (sx, sy)
        self.goal = (gx, gy)

        config.simulating = True
        self.route = []
        self.frontier = deque() if self.mode == 'BFS' else []
        self.visited = set()
        self.current = Node(*self.start, None, [])
        self.enqueued.add(self.start)
        self.frontier.append(self.current)
    
    def step(self) -> bool:
        """
        Performs a single step of the search.

        Returns:
            bool: True if search should continue, false if complete or aborted.
        """
        if not config.simulating:
            return False # Search is stopped externally
        if len(self.frontier) == 0:
            config.simulating = False
            config.failed = True
            return False # Search failed
        
        self.current = self.frontier.popleft() if self.mode == 'BFS' else self.frontier.pop()

        x, y = self.current.x, self.current.y

        # Goal check
        if (x, y) == self.goal:
            self._goal_found()
            return False  # Search has completed successfully

        self.visited.add((x, y))

        # Neighbor Expansion
        self._expansion(x, y)

        return True  # Search should continue
    
    def _goal_found(self) -> None:
        """
        Helper method that traces the route from the goal node back to the start,
        following parent pointers and constructing the final route.
        """
        config.simulating = False
        node = self.current
        while node:
            self.route.append(node)
            node = node.parent

    def _expansion(self, x, y) -> None:
        """
        Helper method that expands outward around a given x, y position, based on self.moves.
        Creates new nodes, and appends them to the frontier, and the set of positions in enqueued.
        """
        for move in self.moves:
            if config.is_valid_pos(x, y, move, self.grid):
                nx, ny = x + move[0], y + move[1]
                if (nx, ny) not in self.visited and (nx, ny) not in self.enqueued:
                    next = Node(nx, ny, self.current, move)
                    self.frontier.append(next)
                    self.enqueued.add((nx, ny))
        
    def get_frontier(self) -> list[list[tuple[int, int]]]:
        """
        Returns the coordinates of nodes currently in the frontier.

        Returns:
            list[list[tuple[int, int]]]: List of [x, y] positions.
        """
        return [[node.x, node.y] for node in self.frontier]

    def get_visited(self) -> list[tuple[int, int]]:
        """
        Returns the coordinates of nodes that have been explored.

        Returns:
            list[tuple[int, int]]: List of visited [x, y] coordinates.
        """
        return list(self.visited)
    
    def get_route(self) -> list[Node]:
        """
        Returns the reconstructed route from start to goal.

        Returns:
            list[Node]: Ordered list of nodes representing the final route.
        """
        return self.route