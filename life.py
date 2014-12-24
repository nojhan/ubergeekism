from copy import copy
from itertools import permutations
import random


def count( node, states, board, graph ):
    """Count the number of neighbours in each given states, in a single pass."""
    nb = {s:0 for s in states}
    for neighbor in graph[node]:
        for state in states:
            if board[neighbor] == state:
                nb[state] += 1
    return nb


class Rule:
    """The template to create a rule for a game of life.

    A rule is just a set of states and a function to compute the state of a given node,
    given the current board states and a neighborhood represented by an adjacency graph."""

    class State:
        default = 0

    # Available states, the first one should be the default "empty" (or "dead") one.
    states = [State.default]

    def __call__(self, node, board, graph ):
        raise NotImplemented


class Conway(Rule):
    """The original rules for Conway's game of life on square grid."""

    class State:
        dead = 0
        live = 1

    states = [State.dead, State.live]

    def __call__(self, node, board, graph ):
        # "a" is just a shortcut.
        a = self.State()
        next = a.dead

        nb = count( node, [a.live], board, graph )
        if board[node] is a.dead:
            if nb[a.live] == 3: # reproduction
                next = a.live
        else: 
            assert(board[node] is a.live)

            if nb[a.live] < 2: # under-population
                next = a.dead
            elif nb[a.live] > 3: # over-population
                next = a.dead
            else: 
                assert( 2 <= nb[a.live] <= 3 )
                next = a.live

        return next


class Goucher(Rule):
    """This is the Goucher 4-states rule.
    It permits gliders on Penrose tiling.
    From: Adam P. Goucher, "Gliders in cellular automata on Penrose tilings", J. Cellular Automata, 2012"""

    class State: # Should be an Enum in py3k
        ground = 0
        head = 1
        tail = 2
        wing = 3

    states = [ State.ground, State.head, State.tail, State.wing ]

    def __call__(self, node, current, graph ):
        """Summarized as:
        ------------------------------------------------------
        | Current state |  Neighbour condition  | Next state |
        ------------------------------------------------------
        |       0       | n1>=1 | n2>=1 |   *   |     3      |
        |       0       | n1>=1 |   *   | n3>=2 |     3      |
        |       1       |   *   |   *   | n3>=1 |     2      |
        |       1       |   *   |   *   |   *   |     1      |
        |       2       |   *   |   *   |   *   |     3      |
        |       *       |   *   |   *   |   *   |     0      |
        ------------------------------------------------------
        """
        # "a" is just a shortcut.
        a = self.State()

        # Default state, if nothing matches.
        next = a.ground

        if current[node] is a.ground:
            # Count the number of neighbors of each state in one pass.
            stated = [a.head,a.tail,a.wing]
            nb = count( node, stated, current, graph )
            # This is the max size of the neighborhood on a rhomb Penrose tiling (P2)
            assert( all(nb[s] <= 11 for s in stated) )

            if nb[a.head] >= 1 and nb[a.tail] >= 1:
                next = a.wing
            elif nb[a.head] >= 1 and nb[a.wing] >= 3:
                next = a.wing

        elif current[node] is a.head:
            # It is of no use to compute the number of heads and tails if the current state is not ground.
            nb = count( node, [a.wing], current, graph )
            assert( all(nb[s] <= 11 for s in [a.wing]) )

            if nb[a.wing] >= 1:
                next = a.tail
            else:
                next = a.head

        elif current[node] is a.tail:
            next = a.wing

        # Default to ground, as stated above.
        # else:
        #     next = a.ground

        return next


def make_board( graph, state = lambda x: 0 ):
    """Create a new board board, filled with the results of the calls to the given state function.
    The given graph should be an iterable with all the nodes.
    The given state function should take a node and return a state.
    The default state function returns zero.
    """
    board = {}
    for node in graph:
        board[node] = state(node)
    return board


def step( current, graph, rule ):
    """Compute one generation of the board.
    i.e. apply the given rule function on each node of the given graph board.
    The given current board should associate a state to a node.
    The given graph should associate each node with its neighbors.
    The given rule is a function that takes a node, the current board and the graph and return the next state of the node."""

    # Defaults to the first state of the rule.
    next = make_board(graph, lambda x : rule.states[0])

    for node in graph:
        next[node] = rule( node, current, graph )

    return next


def play( board, graph, rule, nb_gen ):
    for i in range(nb_gen):
        board = step( board, graph, rule )


if __name__ == "__main__":
    import sys

    # Simple demo on a square grid torus.
    graph = {}
    size = 5
    if len(sys.argv) >= 2:
        size = int(sys.argv[1])

    for i in range(size):
        for j in range(size):

            # All Moore neighborhood around a coordinate.
            neighborhood = set(permutations( [0]+[-1,1]*2, 2)) # FIXME ugly
            assert( len(neighborhood) == 8 )

            graph[(i,j)] = []
            for di,dj in neighborhood:
                # Use modulo to avoid limits and create a torus.
                graph[ (i,j) ].append(( (i+di)%size, (j+dj)%size ))

    rule = Conway()
    # Fill a board with random states.
    board = make_board( graph, lambda x : random.choice(rule.states) )

    # Play and print.
    for i in range(size):
        print i
        for i in range(size):
            for j in range(size):
                print board[(i,j)],
            print ""
        board = step(board,graph,rule)

