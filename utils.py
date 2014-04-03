
import sys
import math

def x( point ):
    return point[0]

def y( point ):
    return point[1]


def LOG( *args ):
    """Print something on stderr and flush"""
    for msg in args:
        sys.stderr.write( str(msg) )
        sys.stderr.write(" ")
        sys.stderr.flush()


def LOGN( *args ):
    """Print something on stdeer, with a trailing new line, and flush"""
    LOG( *args )
    LOG("\n")


def adjacency_from_set( segments ):
    graph = {}
    for start,end in segments:
        graph[start] = graph.get( start, [] )
        graph[start].append( end )
        graph[end]   = graph.get( end,   [] )
        graph[end].append( start )
    return graph


def vertices_from_set( segments ):
    vertices = set()
    for start,end in segments:
        vertices.add(start)
        vertices.add(end)
    return vertices


def tour(lst):
    # consecutive pairs in lst  + last-to-first element
    for a,b in zip(lst, lst[1:] + [lst[0]]):
        yield (a,b)


def euclidian_distance( ci, cj, graph = None):
    return math.sqrt( float(ci[0] - cj[0])**2 + float(ci[1] - cj[1])**2 )

