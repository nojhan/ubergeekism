
import sys
import math
from geometry import x,y

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


def load_points( filename ):
    points = []
    with open(filename) as fd:
        for line in fd:
            if line.strip()[0] != "#":
                p = tuple([float(i) for i in line.split()])
                assert(len(p)==2)
                points.append( p )
    return points


def load_segments( filename ):
    segments = []
    with open(filename) as fd:
        for line in fd:
            if line.strip()[0] != "#":
                edge = [float(i) for i in line.split()]
                assert(len(edge)==4)
                segments.append( ((edge[0],edge[1]),(edge[2],edge[3])) )
    return segments


def load_triangles( filename ):
    triangles = []
    with open(filename) as fd:
        for line in fd:
            if line.strip()[0] != "#":
                tri = [float(i) for i in line.split()]
                assert(len(tri)==6)
                triangles.append( ((tri[0],tri[1]),(tri[2],tri[3]),(tri[4],tri[5])) )
    return triangles


def load_matrix( filename ):
    matrix = {}
    with open(filename) as fd:
        for line in fd:
            if line.strip()[0] != "#":
                skey,svals = line.split(":")
                key = tuple((float(i) for i in skey.split(',')))
                col = {}
                for stri in svals.split():
                    sk,sv = stri.split("=")
                    value = float(sv)
                    k = tuple((float(i) for i in sk.split(",")))
                    col[k] = value
                matrix[key] = col
        assert(len(matrix) == len(matrix[key]))
    return matrix


def load_adjacency( filename ):
    graph = {}
    with open(filename) as fd:
        for line in fd:
            if line.strip()[0] != "#":
                skey,svals = line.split(":")
                key = tuple((float(i) for i in skey.split(',')))
                graph[key] = []
                for sp in svals.split():
                    p = tuple(float(i) for i in sp.split(","))
                    assert(len(p)==2)
                    graph[key].append( p )
    return graph


def adjacency_from_set( segments ):
    graph = {}
    for start,end in segments:
        graph[start] = graph.get( start, [] )
        graph[start].append( end )
        graph[end]   = graph.get( end,   [] )
        graph[end].append( start )
    return graph


def vertices_of( segments ):
    vertices = set()
    for start,end in segments:
        vertices.add(start)
        vertices.add(end)
    return vertices


def tour(lst):
    # consecutive pairs in lst  + last-to-first element
    for a,b in zip(lst, lst[1:] + [lst[0]]):
        yield (a,b)


