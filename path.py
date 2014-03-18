
import math

def euclidian_distance(node, goal):
    def x(node):
        return node[0]
    def y(node):
        return node[1]

    return math.sqrt( (x(node) - x(goal))**2 + (y(node) - y(goal))**2)


def astar(graph, start, goal, cost = euclidian_distance, heuristic = euclidian_distance):
    opened = set()
    closed = set()
    m_heur = {}
    m_parent = {}
    m_cost = {} # path costs

    def path_from(node):
        def parents(node):
            while node:
                yield node
                node = m_parent.get(node, None)
        path  = [p for p in parents(node)]
        cost = m_cost[goal]
        path.reverse()
        return path,cost

    opened.add(start)
    m_cost[start] = 0
    while opened:
        # sort opened nodes based on the heuristic and consider the first one
        current = sorted(opened, key=lambda n : m_heur.get( n, heuristic(n,goal) ) )[0]
        if current == goal:
            return path_from(current)

        closed.add(current)
        opened.remove(current)

        for node in graph[current]:
            if node in closed:
                continue

            elif node in opened:
                next_cost = m_cost[current] + cost(current,node)
                if next_cost < m_cost[node]:
                    m_cost[node] = next_cost
                    m_parent[node] = current
            else:
                m_cost[node] = m_cost[current] + cost(current,node)
                m_heur[node] = heuristic( node, goal )
                m_parent[node] = current
                opened.add(node)
    return []


if __name__ == "__main__":
    print """Graph:
       -1  0     2 : x
      1 o  o-----o
        |  |     |
      0 o--o-----o
           |     |
           |     |
     -2 o--o-----o
      :
      y
      """
    G = {
            ( 0, 0) : [(-1, 0),( 0, 1),( 2, 0),( 0,-2)],
            ( 0, 1) : [( 0, 0),( 2, 1)],
            ( 0,-2) : [( 0, 0),( 2,-2),(-1,-2)],
            (-1, 0) : [(-1, 1),( 0, 0)],
            (-1, 1) : [(-1, 0)],
            (-1,-2) : [( 0,-2)],
            ( 2, 0) : [( 2, 1),( 2,-2),( 0, 0)],
            ( 2, 1) : [( 0, 1),( 2, 0)],
            ( 2,-2) : [( 2, 0),( 0,-2)],
    }

    print "Path from (-1,1) to (-1,-2):"
    path,cost = astar( G, (-1,1), (-1,-2) )
    print "Cost:",cost
    print"Path:",path

