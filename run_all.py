#!/usr/bin/env python
#encoding: utf-8

import os
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
import geometry
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

parser.add_argument('-C', "--cache", help="Try to load available precomputed files instead of computing from scratch",
        default=False, action='store_true')

parser.add_argument('-P', "--noplot-penrose",       help="Do not plot the Penrose tiling",    default=False, action='store_true')
parser.add_argument('-T', "--noplot-tour",          help="Do not plot the TSP tours",         default=False, action='store_true')
parser.add_argument('-M', "--noplot-pheromones",    help="Do not plot the pheromones matrix", default=False, action='store_true')
parser.add_argument('-G', "--noplot-triangulation", help="Do not plot the triangulation",     default=False, action='store_true')
parser.add_argument('-V', "--noplot-voronoi",       help="Do not plot the Voronoï diagram",   default=False, action='store_true')

ask_for = parser.parse_args()

def set_cache( filename, asked = None ):
    fname = filename % ask_for.depth
    if os.path.isfile(fname):
        return fname
    else:
        return asked

if ask_for.cache:
    ask_for.penrose = set_cache( "d%i_penrose.segments", ask_for.penrose )
    ask_for.triangulation = set_cache("d%i_triangulation.triangles", ask_for.triangulation )
    ask_for.tour = [set_cache("d%i_tour.points", ask_for.tour )]
    if ask_for.tour != [None]:
        ask_for.notsp = True
    else:
        ask_for.notsp = False
    ask_for.pheromones = set_cache("d%i_pheromones.mat", ask_for.pheromones )
    ask_for.voronoi = set_cache("d%i_voronoi.graph", ask_for.voronoi )


error_codes = {"NOTSP":100}

depth = ask_for.depth
LOGN( "depth",depth )

########################################################################
# PENROSE TILING
########################################################################

penrose_segments = set()

if ask_for.penrose:
    LOGN( "Load the penrose tiling" )
    with open(ask_for.penrose) as fd:
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

if ask_for.tour != [None]:
    for tour in ask_for.tour:
        with open(tour) as fd:
            trajs.append( utils.load_points(fd) )

if ask_for.notsp:
    if ask_for.tour == [None] or not ask_for.pheromones:
        LOGN( "If you do not want to solve the TSP, you must provide a solution tour (--tour) and a pheromones matrix (--pheromones)" )
        sys.exit(error_codes["NO-TSP"])

    if ask_for.pheromones:
        with open(ask_for.pheromones) as fd:
            phero = utils.load_matrix(fd)

else:
    LOGN( "Solve the TSP with an Ant Colony Algorithm" )

    LOGN( "\tConvert the segment list into an adjacency list graph" )
    G = graph.graph_of( penrose_segments )

    LOGN( "\tCompute a tour" )
    # max_it = 10
    max_it = 2
    # num_ants = 10 #* depth
    num_ants = 2 #* depth
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

if ask_for.triangulation:
    with open(ask_for.triangulation) as fd:
        triangulated = triangulation.load(fd)

else:
    LOGN( "Compute the triangulation of the penrose vertices" )
    points = utils.vertices_of(penrose_segments)
    triangles = triangulation.delaunay_bowyer_watson( points, do_plot = False )

    LOGN( "\tRemove triangles that are not sub-parts of the Penrose tiling" )


    # Filter (i.e. keep) triangles that are strictly acute,
    def strictly_acute(triangle):
        # By excluding edges, we also ensure that no triangle can be collinear nor rectangle,
        return triangulation.is_acute( triangle, exclude_edges = True )
    triangulated_acute = list(filter( strictly_acute, triangles ))
    # A more consise but less readable one-liner would be:
    # triangulated = list(filter( lambda t: triangulation.is_acute( t, exclude_edges = True ), triangles ))

    # def not_collinear(triangle):
    #     return not geometry.collinear(*triangle)
    # triangulated = list(filter( not_collinear, triangulated_acute ))
    triangulated = triangulated_acute

    LOGN( "\t\tRemoved", len(triangles)-len(triangulated), "triangles from", len(triangles))

    with open("d%i_triangulation.triangles" % depth, "w") as fd:
        triangulation.write( triangulated, fd )

triangulation_edges = triangulation.edges_of( triangulated )


########################################################################
# VORONOÏ
########################################################################

voronoi_graph = {}

if ask_for.voronoi:
    with open(ask_for.voronoi) as fd:
        voronoi_graph = graph.load( fd )

else:
    LOGN( "Compute the Voronoï diagram of the triangulation" )
    # Changing the neighborhood to be on vertices instead of edges will not compute the true Voronoï dual graph,
    # but we want this graph to represent the relations on vertices of the tiles.
    voronoi_tri_graph = voronoi.dual(triangulated, neighborhood = voronoi.vertices_neighbours)
    # voronoi_tri_edges   = graph.edges_of(voronoi_tri_graph)
    # voronoi_tri_centers = graph.nodes_of(voronoi_tri_graph)

    LOGN("\tMerge nodes that are both located within a single diamond" )
    LOG("\t\tMerge",len(voronoi_tri_graph),"nodes")
    with open("d%i_voronoi_dual.graph" % depth, "w") as fd:
        graph.write( voronoi_tri_graph, fd )
    voronoi_graph = voronoi.merge_enclosed( voronoi_tri_graph, penrose_segments )
    LOGN("as",len(voronoi_graph),"enclosed nodes")

    with open("d%i_voronoi.graph" % depth, "w") as fd:
        graph.write( voronoi_graph, fd )


voronoi_edges   = graph.edges_of( voronoi_graph )
voronoi_centers = graph.nodes_of( voronoi_graph )


########################################################################
# PLOT
########################################################################

dpi = 600

contrast = [
        ("pheromones",{"edgecolor":"blue"}), # do not specify linewidth and alpha
        ("tour",{"edgecolor":"red","alpha":0.9, "linewidth":3}),
        ("penrose",{"edgecolor":"black", "alpha":0.9, "linewidth":0.9}),
        ("triangulation",{"edgecolor":"green","alpha":0.2,"linewidth":1}),
        ("voronoi_edges",{"edgecolor":"magenta","alpha":1,"linewidth":1}),
        ("voronoi_nodes",{"edgecolor":"magenta","facecolor":"white","alpha":1,"linewidth":1,"s":200}),
]

clean = [
        ("triangulation",{"edgecolor":"lightgreen","alpha":1,"linewidth":0.5}),
        ("pheromones",{"edgecolor":"#ffcc00"}),
        ("tour",{"edgecolor":"#7777dd","alpha":0.7, "linewidth":2.5}),
        ("penrose",{"edgecolor":"black", "alpha":1, "linewidth":0.3}),
        ("voronoi_edges",{"edgecolor":"blue","alpha":0.4,"linewidth":1}),
        ("voronoi_nodes",{"edgecolor":"blue","facecolor":"white","alpha":0.4,"linewidth":1.5,"s":250}),
]

chosen_theme = clean

# Rebuild the theme from the chosen one and add zorder using the order given in the theme.
theme = {}
for i in range(len(chosen_theme)):
    k = chosen_theme[i][0]
    theme[k] = chosen_theme[i][1]
    theme[k]["zorder"] = i


LOGN( "Plot the image" )
fig = plot.figure()
ax = fig.add_subplot(111)

if not ask_for.noplot_pheromones:
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
            uberplot.plot_segments( ax, seg, alpha=0.01*nph, linewidth=1*nph, **theme["pheromones"] )
            # uberplot.scatter_segments( ax, seg, color="red", alpha=0.5, linewidth=nph )

if not ask_for.noplot_tour:
    for traj in trajs:
        LOGN( "\ttraj",len(traj),"points" )
        # best tour
        uberplot.plot_segments( ax, utils.tour(traj), **theme["tour"])

if not ask_for.noplot_penrose:
    LOGN( "\ttiling",len(penrose_segments),"segments" )
    uberplot.plot_segments( ax, penrose_segments, **theme["penrose"])

if not ask_for.noplot_triangulation:
    LOGN( "\ttriangulation",len(triangulation_edges),"edges" )
    uberplot.plot_segments( ax, triangulation_edges, **theme["triangulation"])

if not ask_for.noplot_voronoi:
    LOGN( "\tVoronoï",len(voronoi_edges),"edges")
    # uberplot.plot_segments( ax, voronoi_tri_edges, edgecolor="red", alpha=1, linewidth=1 )
    # uberplot.scatter_points( ax, voronoi_tri_centers, edgecolor="red", facecolor="white", s=200, alpha=1, zorder=10 )
    uberplot.plot_segments(  ax, voronoi_edges,   **theme["voronoi_edges"] )
    uberplot.scatter_points( ax, voronoi_centers, **theme["voronoi_nodes"] )

ax.set_aspect('equal')


# transparent background in SVG
fig.patch.set_visible(False)
ax.axis('off')
plot.savefig("ubergeekism_d%i.svg" % depth, dpi=dpi)

fig.patch.set_visible(True)
fig.patch.set_facecolor('white')
plot.savefig("ubergeekism_d%i.png" % depth, dpi=dpi)

plot.show()

