#/usr/bin/env python

from utils import tour,LOG,LOGN,x,y
import triangulation

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


def neighbours( triangle, polygons ):
    """Returns the set of triangles in candidates that have an edge in common with the given triangle."""
    for polygon in polygons:
        if polygon == triangle:
            continue

        # Convert list of points to list of edges, because we want to find EDGE neighbours.
        edges_poly = list(tour(list(polygon )))
        assert( len(list(edges_poly)) > 0 )
        edges_tri  = list(tour(list(triangle)))
        assert( len(list(edges_tri)) > 0 )

        # If at least one of the edge that are in availables polygons are also in the given triangle.
        # Beware the symetric edges.
        # if any( edge_in( edge, edges_tri ) for edge in edges_poly ):
        #     yield polygon
        for edge in edges_poly:
            if edge_in( edge, edges_tri ):
                yield polygon
                break


def dual( triangles ):
    graph = {}

    def add_edge( current, neighbor ):
        if current in graph:
            if neighbor not in graph[current]:
                graph[current].append( neighbor )
        else:
            graph[current] = [ neighbor ]

    for triangle in triangles:
        assert( len(triangle) == 3 )
        current_node = triangulation.circumcircle(triangle)[0]
        assert( len(current_node) == 2 )

        for neighbor_triangle in neighbours( triangle, triangles ):
            neighbor_node = triangulation.circumcircle(neighbor_triangle)[0]
            assert( len(neighbor_node) == 2 )

            add_edge(  current_node, neighbor_node )
            add_edge( neighbor_node,  current_node )

    return graph


def edges_of( graph ):
    # edges = set()
    edges = []
    for k in graph:
        for n in graph[k]:
            if k != n and (k,n) not in edges and (n,k) not in edges:
                # edges.add( (k,n) )
                edges.append( (k,n) )

    return edges


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
    voronoi_edges = edges_of( voronoi_graph )
    print voronoi_edges

    ax = fig.add_subplot(111)
    ax.set_aspect('equal')
    uberplot.scatter_segments( ax, delaunay_edges, facecolor = "blue" )
    uberplot.plot_segments( ax, delaunay_edges, edgecolor = "blue" )
    uberplot.scatter_segments( ax, voronoi_edges, facecolor = "red" )
    uberplot.plot_segments( ax, voronoi_edges, edgecolor = "red" )
    plot.show()

