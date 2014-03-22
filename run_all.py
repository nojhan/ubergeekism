#!/usr/bin/env python

import sys
import turtle
import lindenmayer
import utils
import ants
import shortpath
import uberplot
import matplotlib.pyplot as plot

depth = 1
if len(sys.argv) > 1:
    depth = int( sys.argv[1] )
print "depth",depth

print "Draw the penrose tesselation"

segment_size = 10
float_rounding = 10

ttl = turtle.Turtle()
ttl.speed('fastest')
penrose = lindenmayer.DumpTurtleLSystem(ttl, 
        axiom="[X]++[X]++[X]++[X]++[X]", 
        rules={
            'F': "",
            'W': "YF++ZF----XF[-YF----WF]++",
            'X': "+YF--ZF[---WF--XF]+",
            'Y': "-WF++XF[+++YF++ZF]-",
            'Z': "--YF++++WF[+ZF++++XF]--XF"
        }, 
        angle=36, heading=0, size=segment_size, rounding=float_rounding )

# actually do something
penrose.draw( depth )
print "segments",len(penrose.segments)
with open("penrose_%i.segments" % depth, "w") as fd:
    fd.write( str(penrose) )

print "Convert the segment list into an adjacency list graph"
G = utils.adjacency_from_set( penrose.segments )


print "Solve the TSP with an Ant Colony Algorithm"

max_it = 10
num_ants = 10 #* depth
decay = 0.1
w_heur = 2.5
w_local_phero = 0.1
c_greed = 0.9
w_history = 1.0

best,phero = ants.search( G, max_it, num_ants, decay, w_heur, w_local_phero, w_history, c_greed, cost_func = ants.graph_distance )

print "Transform the resulting nodes permutation into a path on the graph"
# by finding the shortest path between two cities.
traj = []
for start,end in ants.tour(best["permutation"]):
    p,c = shortpath.astar( G, start, end )
    traj += p
print "traj",len(traj)

print "Plot the resulting tour"
fig = plot.figure()
ax = fig.add_subplot(111)

maxph=0
for i in phero:
    maxph = max( maxph, max(phero[i].values()))

# ant colony
# pheromones
for i in phero:
    for j in phero[i]:
        if i == j:
            continue
        nph = phero[i][j]/maxph
        seg = [(i,j)]
        # print nph,seg
        uberplot.plot_segments( ax, seg, edgecolor="blue", alpha=0.01*nph, linewidth=1*nph )
        # uberplot.scatter_segments( ax, seg, color="red", alpha=0.5, linewidth=nph )

# best tour
uberplot.plot_segments( ax, ants.tour(traj), color="red",  alpha=0.9, linewidth=3 )

# tesselation
tcol = "black"
uberplot.plot_segments( ax, penrose.segments, edgecolor=tcol, alpha=0.9, linewidth=1 )
uberplot.scatter_segments( ax, penrose.segments,  color=tcol, alpha=0.9, linewidth=1 )

ax.set_aspect('equal')

plot.show()

