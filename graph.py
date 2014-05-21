
from geometry import x,y

def graph_of( segments ):
    graph = {}
    for start,end in segments:
        graph[start] = graph.get( start, [] )
        graph[start].append( end )
        graph[end]   = graph.get( end,   [] )
        graph[end].append( start )
    return graph


def edges_of( graph ):
    edges = set()
    for k in graph:
        for n in graph[k]:
            if k != n and (k,n) not in edges and (n,k) not in edges:
                edges.add( (k,n) )
    return list(edges)


def nodes_of( graph ):
    return graph.keys()


def load( stream ):
    graph = {}
    for line in stream:
        if line.strip()[0] != "#":
            skey,svals = line.split(":")
            key = tuple((float(i) for i in skey.split(',')))
            graph[key] = []
            for sp in svals.split():
                p = tuple(float(i) for i in sp.split(","))
                assert(len(p)==2)
                graph[key].append( p )
    return graph


def write( graph, stream ):
    for k in graph:
        stream.write( "%f,%f:" % (x(k),y(k)) )
        for p in graph[k]:
            stream.write( "%f,%f " % (x(p),y(p)) )
        stream.write("\n")

