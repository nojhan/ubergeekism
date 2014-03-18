
def graph( segments ):
    graph = {}
    for start,end in segments:
        graph[start] = graph.get( start, [] ).append( end )
        graph[end]   = graph.get( end,   [] ).append( start )
    return graph

