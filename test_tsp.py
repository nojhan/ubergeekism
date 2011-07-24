
from tsplib import *


segments = [
        ( (0,0),(0,2) ),
        ( (0,2),(2,2) ),
        ( (2,2),(2,0) ),
        ( (2,0),(0,0) )
]

filename = "test.tsp"
with open(filename,"w") as fd:
    write_segments( segments, fd=fd, size=1, depth=0, rounding=10 )
    write_segments( segments, fd=sys.stdout, size=1, depth=0, rounding=10 )

with open(filename,"r") as fd:
    nodes = read_nodes( fd )

print "Nodes: id (x, y)"
for idx,node in nodes.items():
    print idx,node

with open(filename,"r") as fd:
    vertices = read_vertices( fd )

print "Segments: (x1,y1) (x2,y2)"
segments = []
for i1,i2 in vertices:
    print nodes[i1],nodes[i2]
    segments.append( (nodes[i1],nodes[i2]) )

plot_segments( segments )


