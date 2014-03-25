
import sys
import argparse

import matplotlib.pyplot as plot
from matplotlib.path import Path
import matplotlib.patches as patches


def parse_segments( filename ):
    segments = []
    with open( filename ) as fd:
        for line in fd:
            edge = [ float(i) for i in line.split() ]
            if len(edge) == 4:
                start = (edge[0],edge[1])
                end = (edge[2],edge[3])
                segments.append( (start,end) )
    return segments


def plot_segments( ax, segments, **kwargs ):
    for start,end in segments:
        verts = [start,end,(0,0)]
        codes = [Path.MOVETO,Path.LINETO,Path.STOP]
        path = Path(verts, codes)
        patch = patches.PathPatch(path, facecolor='none', **kwargs )
        ax.add_patch(patch)


def scatter_segments( ax, segments, **kwargs  ):
    xy = [ ((i[0],j[0]),(i[1],j[1])) for (i,j) in segments]
    x = [i[0] for i in xy]
    y = [i[1] for i in xy]
    ax.scatter( x,y, s=20, marker='o', **kwargs)


if __name__=="__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('-s', "--segments", default=[None], action='store', type=str, nargs='*')

    args = parser.parse_args()

    fig = plot.figure()
    ax = fig.add_subplot(111)

    if args.segments != [None]:
        for filename in args.segments:
            seg = parse_segments(filename)
            scatter_segments( ax, seg, edgecolor="red" )
            plot_segments( ax, seg, edgecolor="blue" )

    plot.show()
