#/usr/bin/env python
#encoding: utf-8

from utils import tour,LOG,LOGN,x,y
import triangulation
import geometry
import graph

def nodes( triangles ):
    """Compute the locations of the centers of all the circumscribed circles of the given triangles"""
    for triangle in triangles:
        (cx,cy),r = triangulation.circumcircle(triangle)
        yield (cx,cy)


def edge_in( edge, edges ):
    """Return True if the given edge (or its symetric) is in the given polygon."""
    n,m = edge
    assert( len(n) == 2 )
    assert( len(m) == 2 )
    return (n,m) in edges or (m,n) in edges


def neighbours( candidate, polygons ):
    """Returns the set of candidates in candidates that have an edge in common with the given candidate."""
    for polygon in polygons:
        if polygon == candidate:
            continue

        # Convert list of points to list of edges, because we want to find EDGE neighbours.
        edges_poly = list(tour(list(polygon)))
        assert( len(list(edges_poly)) > 0 )
        edges_can  = list(tour(list(candidate)))
        assert( len(list(edges_can)) > 0 )

        # If at least one of the edge that are in availables polygons are also in the given candidate.
        # Beware the symetric edges.
        for edge in edges_poly:
            # We use yield within the loop, because we want to test all the candidate edges and
            # return all the matching ones.
            if edge_in( edge, edges_can ):
                yield polygon
                break


def dual( triangles ):
    """Compute the dual Voronoï graph of a triangulation."""
    graph = {}

    def add_edge( current, neighbor ):
        if current in graph:
            if neighbor not in graph[current]:
                graph[current].append( neighbor )
        else:
            graph[current] = [ neighbor ]

    for triangle in triangles:
        assert( len(triangle) == 3 )
        assert( not geometry.collinear(*triangle) )
        assert( triangulation.is_acute(triangle) )
        # Consider the center of the circumcircle as the node for this triangle.
        current_node = triangulation.circumcircle(triangle)[0]
        assert( len(current_node) == 2 )

        for neighbor_triangle in neighbours( triangle, triangles ):
            assert( len(triangle) == 3 )
            assert( not geometry.collinear(*neighbor_triangle) )
            assert( triangulation.is_acute(neighbor_triangle) )
            # Consider the neighbor's center as nodes.
            neighbor_node = triangulation.circumcircle(neighbor_triangle)[0]
            assert( len(neighbor_node) == 2 )

            # Add edges between the current triangle's node and thoses of its neighbors.
            add_edge(  current_node, neighbor_node )
            add_edge( neighbor_node,  current_node )

    return graph


def merge_nodes( graph, n0, n1, n2 ):
    """Merge n0 and n1 nodes as n2 within the given graph."""

    # Assert that the old nodes are in the graph
    # and that they are linked by an edge.
    assert( n0 in graph )
    assert( n1 in graph[n0] )
    assert( n1 in graph )
    assert( n0 in graph[n1] )
    assert( n0 != n1 )

    # Remove and save the neigbhours of the old nodes.
    n0_ngb = graph.pop(n0)
    n1_ngb = graph.pop(n1)
    # Insert the new node along with the old neighbours.
    # We use a set to ensure that there is no duplicated nodes.
    neighbours = list(set(n0_ngb + n1_ngb))
    # Filter out duplicate of the considered nodes.
    # Because the new node cannot be linked to the old nodes, nor to itself.
    graph[n2] = filter( lambda n: n not in (n0,n1,n2), neighbours )

    for node in graph:
        # Replace occurences of old nodes as neighbours by the new node.
        while n0 in graph[node]:
            graph[node].remove(n0)
            graph[node].append(n2)
        while n1 in graph[node]:
            graph[node].remove(n1)
            graph[node].append(n2)

    # assert that any neighbour is also a node of the graph.
    for node in graph:
        for neighbour in graph[node]:
            assert( neighbour in graph )
            assert( neighbour != node )

    return graph


def merge_enclosed( graph, segments ):
    """Merge nodes of the given graph that are on edges that do not intersects with the given segments."""
    i=0
    while i < len(graph.keys()):
        node = graph.keys()[i]
        j=0
        altered = False
        while j < len(graph[node]):
            neighbour = graph[node][j]
            assert( neighbour in graph )
            edge = (node,neighbour)

            if not any( geometry.segment_intersection(edge,seg) for seg in segments ):
                graph = merge_nodes( graph, edge[0], edge[1], geometry.middle(*edge) )
                altered = True
                LOG(".")
                break
            else:
                j+=1
                continue

        if altered:
            i = 0
        else:
            i+=1

    return graph


if __name__ == "__main__":
    import sys
    import random
    import utils
    import uberplot
    import triangulation
    import matplotlib.pyplot as plot

    if len(sys.argv) > 1:
        scale = 100
        nb = int(sys.argv[1])
        points = [ (scale*random.random(),scale*random.random()) for i in range(nb)]
    else:
        points = [
                (0,40),
                (100,60),
                (40,0),
                (50,100),
                (90,10),
                # (50,50),
                ]

    fig = plot.figure()

    triangles = triangulation.delaunay_bowyer_watson( points )
    delaunay_edges = triangulation.edges_of( triangles )

    voronoi_graph = dual( triangles )
    voronoi_edges = graph.edges_of( voronoi_graph )
    print voronoi_edges

    ax = fig.add_subplot(111)
    ax.set_aspect('equal')
    uberplot.scatter_segments( ax, delaunay_edges, facecolor = "blue" )
    uberplot.plot_segments( ax, delaunay_edges, edgecolor = "blue" )
    uberplot.scatter_segments( ax, voronoi_edges, facecolor = "red" )
    uberplot.plot_segments( ax, voronoi_edges, edgecolor = "red" )
    plot.show()

