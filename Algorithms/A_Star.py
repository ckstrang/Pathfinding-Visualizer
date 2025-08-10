import Core.config as config
import heapq

class Node:
    def __init__(self, x, y, parent, move, g, h):
        self.x = x
        self.y = y
        self.parent = parent
        self.move = move
        self.g = g
        self.h = h
        self.f = g + h
    
    def __lt__(self, other):
        return self.f < other.f

class Pathfinder:
    """
    Implements weighted A* on a 2D grid.

    Attributes:
        grid (list[list[str]]): The grid environment.
        moves (list[tuple[int, int]]): The list of moves based on selected movement type.
        start (tuple[int, int]): The starting coordinates for the search.
        goal (tuple[int, int]): The goal coordinates for the search.
        heuristic (str): The heuristic to use for calculating h.
        w (int): The weight of the heuristic.
        route (list[Node]): List of nodes along the solution route.
        frontier (heapq): Priority queue of nodes to be visited.
        enqueued (set[tuple[int, int]]): Set of coordinates that have been enqueued into the frontier.
        visited (set[tuple[int, int]]): Set of coordinates that have been visited.
        counter (int): counter used for the frontier.
        current (Node): The node currently being explored.
    """
    def __init__(self, grid, sx, sy, gx, gy, heuristic, w):
        """
        Initializes the Search object and begins the simulation.

        Args:
            grid (list[list[str]]): The grid environment.
            sx, sy      (int, int): Starting coordinates of the search agent.
            gx, gy      (int, int): Goal coordinates.
            heuristic        (str): The heuristic to use.
            w                (int): Weight of the heuristic.
        """
        self.grid = grid
        self.moves = config.get_moves(config.movement_type)
        self.start = (sx, sy)
        self.goal = (gx, gy)
        self.heuristic = heuristic
        self.w = w

        config.simulating = True
        self.route = []
        self.frontier = []
        self.enqueued = set()
        self.visited = set()
        self.counter = 0
        self.current = Node(*self.start, None, [], 0, self.compute_h(*self.start, *self.goal))
        self.enqueued.add(self.start)
        heapq.heappush(self.frontier, (self.current.f, self.counter, self.current))
        self.counter += 1

    def compute_h(self, x, y, gx, gy):
        """
        Computes and returns h(n) of any given x, y position relative to a given goal position.

        Parameters:
            x, y   (int, int): Coordinates of given position.
            gx, gy (int, int): Coordinates of goal position.
        
        Returns:
            int              : Computed estimate.
        """
        if self.heuristic == 'Diagonal':
            dx = abs(x - gx)
            dy = abs(y - gy)
            return (100 * (dx + dy) + (141 - 2 * 100) * min(dx,dy)) * self.w
        elif self.heuristic == 'Manhattan':
            return (100 * (abs(x-gx) + abs(y-gy))) * self.w
        else:
            return 0

    def step(self):
        """
        Performs a single iteration of the search.

        Returns:
            bool: True if search should continue, false if complete or aborted.
        """
        if not config.simulating:
            return False # Search is stopped externally
        if len(self.frontier) == 0:
            config.simulating = False
            return False # Search failed
        
        self.current = heapq.heappop(self.frontier)[2]
        x, y = self.current.x, self.current.y

        # Goal check
        if (x, y) == self.goal:
            self._goal_found()
            return False # Search completed successfully

        self.visited.add((x,y))

        # Neighbor Expansion
        self._expansion(x, y)
        
        return True  # Search should continue
    
    def _goal_found(self):
        """
        Helper method that traces the route from the goal node back to the start,
        following parent pointers and constructing the final route.
        """
        config.simulating = False
        node = self.current
        while node:
            self.route.append(node)
            node = node.parent
    
    def _expansion(self, x, y):
        """
        Helper method that expands outward around a given x, y position, based on self.moves.
        Creates new nodes, and adds them to the frontier, and the set of positions in enqueued.
        """
        for move in self.moves:
            if config.is_valid_pos(x, y, move, self.grid):
                nx = x + move[0]
                ny = y + move[1]
                g = config.get_move_cost(move)
                if (nx, ny) not in self.visited and (nx, ny) not in self.enqueued:
                    nextNode = Node(nx, ny, self.current, move, self.current.g + g, self.compute_h(nx, ny, *self.goal))
                    heapq.heappush(self.frontier, (nextNode.f, self.counter, nextNode))
                    self.counter += 1
                    self.enqueued.add((nx, ny))

    def get_frontier(self):
        """
        Returns the coordinates of nodes currently in the frontier.

        Returns:
            list[list[int, int]]: List of [x, y] positions.
        """
        return [[node[2].x, node[2].y] for node in self.frontier]

    def get_visited(self):
        """
        Returns the coordinates of nodes that have been visited.

        Returns:
            list[tuple[int, int]]: List of visited [x, y] coordinates.
        """
        return list(self.visited)
    
    def get_route(self):
        """
        Returns the reconstructed route from start to goal.

        Returns:
            list[Node]: Ordered list of nodes representing the final route.
        """
        return self.route