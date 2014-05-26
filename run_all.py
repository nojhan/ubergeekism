#!/usr/bin/env python
#encoding: utf-8

import sys
import turtle
import argparse
import matplotlib.pyplot as plot
from itertools import ifilterfalse as filter_if_not

import ants
import utils
from utils import LOG,LOGN
from geometry import x,y
import hull
import uberplot
import shortpath
import lindenmayer
import triangulation
import voronoi
import graph

parser = argparse.ArgumentParser()

parser.add_argument('-p', "--penrose", help="Do not compute the Penrose tiling but load it from a file",
        default=None, action='store', type=str, metavar="SEGMENTS")
parser.add_argument( '-d', '--depth', help="Recursive depth of the Lindenmayer computations = size of the Penrose tiling",
        default=1, type=int, metavar="DEPTH")

parser.add_argument('-t', "--notsp", help="Do not compute the TSP",
        default=False, action='store_true')
parser.add_argument('-r', "--tour", help="Load several TSP tour from a file",
        default=[None], action='store', type=str, nargs="*", metavar="POINTS")
parser.add_argument('-m', "--pheromones", help="Load a pheromones matrix from a file",
        default=None, action='store', type=str, metavar="MATRIX")

parser.add_argument('-g', "--triangulation", help="Do not compute the Delaunay triangulation but load it from a file",
        default=None, action='store', type=str, metavar="SEGMENTS")
parser.add_argument('-v', "--voronoi", help="Do not compute the Voronoï diagram but load it from a file",
        default=None, action='store', type=str, metavar="POINTS")

args = parser.parse_args()


error_codes = {"NOTSP":100}

depth = args.depth
LOGN( "depth",depth )

########################################################################
# PENROSE TILING
########################################################################

penrose_segments = set()

if args.penrose:
    LOGN( "Load the penrose tiling" )
    with open(args.penrose) as fd:
        penrose_segments = utils.load_segments(fd)

else:
    LOGN( "Draw the penrose tiling" )


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

    # save this intermediate step
    penrose_segments = penrose.segments
    LOGN( "\tsegments",len(penrose_segments) )
    with open("d%i_penrose.segments" % depth, "w") as fd:
        utils.write_segments( penrose_segments, fd )



########################################################################
# TSP
########################################################################

trajs = []

if args.tour != [None]:
    for tour in args.tour:
        with open(tour) as fd:
            trajs.append( utils.load_points(fd) )

if args.notsp:
    if args.tour == [None] or not args.pheromones:
        LOGN( "If you do not want to solve the TSP, you must provide a solution tour (--tour) and a pheromones matrix (--pheromones)" )
        sys.exit(error_codes["NO-TSP"])

    if args.pheromones:
        with open(args.pheromones) as fd:
            phero = utils.load_matrix(fd)

else:
    LOGN( "Solve the TSP with an Ant Colony Algorithm" )

    LOGN( "\tConvert the segment list into an adjacency list graph" )
    G = graph.graph_of( penrose_segments )

    LOGN( "\tCompute a tour" )
    max_it = 10
    num_ants = 10 #* depth
    decay = 0.1
    w_heur = 2.5
    w_local_phero = 0.1
    c_greed = 0.9
    w_history = 1.0

    best,phero = ants.search( G, max_it, num_ants, decay, w_heur, w_local_phero, w_history, c_greed, cost_func = ants.graph_distance )

    LOGN( "\tTransform the resulting nodes permutation into a path on the graph" )
    # by finding the shortest path between two cities.
    traj = []
    for start,end in utils.tour(best["permutation"]):
        p,c = shortpath.astar( G, start, end )
        traj += p
    trajs.append(traj)

    with open("d%i_tour.points" % depth, "w") as fd:
        utils.write_points( traj, fd )

    with open("d%i_pheromones.mat" % depth, "w") as fd:
        utils.write_matrix( phero, fd )


########################################################################
# TRIANGULATION
########################################################################

triangulated = []

if args.triangulation:
    with open(args.triangulation) as fd:
        triangulated = triangulation.load(fd)

else:
    LOGN( "Compute the triangulation of the penrose vertices" )
    points = utils.vertices_of(penrose_segments)
    triangles = triangulation.delaunay_bowyer_watson( points, do_plot = False )

    LOGN( "\tRemove triangles that are not sub-parts of the Penrose tiling" )

    # Filter out triangles that are obtuse
    triangulated = list(filter_if_not( triangulation.is_acute, triangles ))
    LOGN( "\t\tRemoved", len(triangles)-len(triangulated), "triangles" )

    with open("d%i_triangulation.triangles" % depth, "w") as fd:
        triangulation.write( triangulated, fd )

triangulation_edges = triangulation.edges_of( triangulated )


########################################################################
# VORONOÏ
########################################################################

voronoi_graph = {}

if args.voronoi:
    with open(args.voronoi) as fd:
        voronoi_graph = graph.load( fd )

else:
    LOGN( "Compute the Voronoï diagram of the triangulation" )
    voronoi_tri_graph = voronoi.dual(triangulated)
    # voronoi_tri_edges   = graph.edges_of(voronoi_tri_graph)
    # voronoi_tri_centers = graph.nodes_of(voronoi_tri_graph)

    LOGN("\tMerge nodes that are both located within a single diamond" )
    LOG("\t\tMerge",len(voronoi_graph),"nodes")
    voronoi_graph = voronoi.merge_enclosed( voronoi_tri_graph, penrose_segments )
    LOGN("as",len(voronoi_graph),"enclosed nodes")

    with open("d%i_voronoi.graph" % depth, "w") as fd:
        graph.write( voronoi_graph, fd )


voronoi_edges   = graph.edges_of( voronoi_graph )
voronoi_centers = graph.nodes_of( voronoi_graph )


########################################################################
# PLOT
########################################################################

LOGN( "Plot the resulting tour" )
fig = plot.figure()
ax = fig.add_subplot(111)

LOGN( "\tpheromones",len(phero),"nodes" )#,"x",len(phero[traj[0]]) )
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
        # LOGN( nph,seg )
        uberplot.plot_segments( ax, seg, edgecolor="blue", alpha=0.01*nph, linewidth=1*nph )
        # uberplot.scatter_segments( ax, seg, color="red", alpha=0.5, linewidth=nph )

for traj in trajs:
    LOGN( "\ttraj",len(traj),"points" )
    # best tour
    uberplot.plot_segments( ax, utils.tour(traj), edgecolor="red",  alpha=0.9, linewidth=3 )

LOGN( "\ttiling",len(penrose_segments),"segments" )
tcol = "black"
uberplot.plot_segments( ax, penrose_segments, edgecolor=tcol, alpha=0.9, linewidth=2 )
uberplot.scatter_segments( ax, penrose_segments, edgecolor=tcol, alpha=0.9, linewidth=1 )

# triangulation
LOGN( "\ttriangulation",len(triangulation_edges),"edges" )
uberplot.plot_segments( ax, triangulation_edges, edgecolor="green", alpha=0.2, linewidth=1 )

# Voronoï
LOGN( "\tVoronoï",len(voronoi_edges),"edges")
uberplot.scatter_points( ax, voronoi_centers, edgecolor="magenta", facecolor="white", s=200, alpha=1 )
uberplot.plot_segments( ax, voronoi_edges, edgecolor="magenta", alpha=1, linewidth=1 )

ax.set_aspect('equal')


# transparent background in SVG
fig.patch.set_visible(False)
ax.axis('off')
plot.savefig("ubergeekism.svg", dpi=600)

ax.axis('off')
fig.patch.set_visible(True)
fig.patch.set_facecolor('white')
plot.savefig("ubergeekism.png", dpi=600)
plot.show()

