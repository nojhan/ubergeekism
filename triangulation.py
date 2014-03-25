
import sys
import math
from utils import tour,LOG,LOGN
from itertools import ifilterfalse as filter_if_not

# Based on http://paulbourke.net/papers/triangulate/
# Efficient Triangulation Algorithm Suitable for Terrain Modelling
#     An Algorithm for Interpolating Irregularly-Spaced Data
#     with Applications in Terrain Modelling
# Written by Paul Bourke
# Presented at Pan Pacific Computer Conference, Beijing, China.
# January 1989

def x( point ):
    return point[0]

def y( point ):
    return point[1]

def mid( xy, pa, pb ):
    return ( xy(pa) + xy(pb) ) / 2.0

def middle( pa, pb ):
    return mid(x,pa,pb),mid(y,pa,pb)

def mtan( pa, pb ):
    return -1 * ( x(pa) - x(pb) ) / ( y(pa) - y(pb) )


class CoincidentPointsError(Exception):
    """Coincident points"""
    pass

def circumcircle( triangle, epsilon = sys.float_info.epsilon ):
    """Compute the circumscribed circle of a triangle and 
    Return a 2-tuple: ( (center_x, center_y), radius )"""

    assert( len(triangle) == 3 )
    p0,p1,p2 = triangle
    assert( len(p0) == 2 )
    assert( len(p1) == 2 )
    assert( len(p2) == 2 )

    dy01 = abs( y(p0) - y(p1) )
    dy12 = abs( y(p1) - y(p2) )

    if dy01 < epsilon and dy12 < epsilon:
        # coincident points
        raise CoincidentPointsError

    elif dy01 < epsilon:
        m12 = mtan( p2,p1 )
        mx12,my12 = middle( p1, p2 )
        cx = mid( x, p1, p0 )
        cy = m12 * (cx - mx12) + my12

    elif dy12 < epsilon:
        m01 = mtan( p1, p0 )
        mx01,my01 = middle( p0, p1 )
        cx = mid( x, p2, p1 )
        cy = m01 * ( cx - mx01 ) + my01

    else:
        m01 =  mtan( p1, p0 )
        m12 =  mtan( p2, p1 )
        mx01,my01 = middle( p0, p1 )
        mx12,my12 = middle( p1, p2 )
        cx = ( m01 * mx01 - m12 * mx12 + my12 - my01 ) / ( m01 - m12 )
        if dy01 > dy12:
            cy = m01 * ( cx - mx01 ) + my01
        else:
            cy = m12 * ( cx - mx12 ) + my12

    dx1 = x(p1) - cx
    dy1 = y(p1) - cy
    r = math.sqrt(dx1**2 + dy1**2)

    return (cx,cy),r


def in_circle( p, center, radius, epsilon  = sys.float_info.epsilon ):
    """Return True if the given point p is in the circumscribe circle of the given triangle"""

    assert( len(p) == 2 )
    cx,cy = center

    dxp = x(p) - cx
    dyp = y(p) - cy
    dr = math.sqrt(dxp**2 + dyp**2)

    if (dr - radius) <= epsilon:
        return True
    else:
        return False


def in_circumcircle( p, triangle, epsilon  = sys.float_info.epsilon ):
    """Return True if the given point p is in the circumscribe circle of the given triangle"""

    assert( len(p) == 2 )
    (cx,cy),r = circumcircle( triangle, epsilon )
    return in_circle( p, (cx,cy), r, epsilon )


def bounds( vertices ):
    # find vertices set bounds
    xmin = x(vertices[0])
    ymin = y(vertices[0])
    xmax = xmin
    ymax = ymin

    # we do not use min(vertices,key=x) because it would iterate 4 times over the list, instead of just one
    for v in vertices:
        xmin = min(x(v),xmin)
        xmax = max(x(v),xmax)
        ymin = min(y(v),ymin)
        ymax = max(y(v),ymax)
    return (xmin,ymin),(xmax,ymax)


def edges_of( triangulation ):
    edges = []
    for t in triangulation:
        for e in utils.tour(list(t)):
            edges.append( e )
    return edges


def delaunay_bowyer_watson( points, epsilon = sys.float_info.epsilon, supert=20, do_plot = True ):

    if do_plot and len(points) > 10:
        print "WARNING it is a bad idea to plot each steps of a triangulation of many points"
        return []

    # sort points first on the x-axis, then on the y-axis
    vertices = sorted( points )

    (xmin,ymin),(xmax,ymax) = bounds( vertices )

    dx = xmax - xmin
    dy = ymax - ymin
    dmax = max( dx, dy )
    xmid = (xmax + xmin) / 2.0
    ymid = (ymax + ymin ) / 2.0


    # compute the super triangle, that encompasses all the vertices
    supertri = ( (xmid-supert*dmax, ymid-dmax ),
                 (xmid, ymid+supert*dmax),
                 (xmid+supert*dmax, ymid-dmax) )

    LOGN( "super-triangle",supertri )

    # it is the first triangle of the list
    triangles = [ supertri ]

    completed = { supertri: False }

    # The predicate returns true if at least one of the vertices
    # is also found in the supertriangle
    def match_supertriangle( tri ):
        if tri[0] in supertri or \
           tri[1] in supertri or \
           tri[2] in supertri:
            return True

    # insert vertices one by one
    it=0
    for vi,vertex in enumerate(vertices):
        LOGN( "\tvertex",vertex )
        assert( len(vertex) == 2 )

        if do_plot:
            fig = plot.figure()
            ax = fig.add_subplot(111)
            scatter_x = [ p[0] for p in vertices[:vi]+list(supertri)]
            scatter_y = [ p[1] for p in vertices[:vi]+list(supertri)]
            ax.scatter( scatter_x,scatter_y, s=30, marker='o', facecolor="black")
            ax.scatter( vertex[0],vertex[1], s=30, marker='o', facecolor="red")
            uberplot.plot_segments( ax, edges_of(triangles), edgecolor = "blue", alpha=0.3, linestyle='dashed' )

        # All the triangles whose circumcircle encloses the point to be added are identified,
        # the outside edges of those triangles form an enclosing polygon.

        # forget previous candidate polygon's edges
        enclosing = []

        removed = []
        for triangle in triangles:
            LOGN( "\t\ttriangle",triangle )
            assert( len(triangle) == 3 )

            # if completed has a key, test it, else return False
            if completed.get( triangle, False ):
                LOGN( "\t\t\tAlready completed" )
                # if do_plot:
                    # uberplot.plot_segments( ax, tour(list(triangle)), edgecolor = "magenta", alpha=1, lw=1, linestyle='dotted' )
                continue

            LOGN( "\t\t\tCircumcircle" ) 
            assert( triangle[0] != triangle[1] and triangle[1] != triangle [2] and triangle[2] != triangle[0] )
            center,radius = circumcircle( triangle, epsilon )

            # if it match Delaunay's conditions
            if x(center) < x(vertex) and math.sqrt((x(vertex)-x(center))**2) > radius:
                LOGN( "\t\t\tMatch Delaunay, mark as completed" ) 
                completed[triangle] = True

            # if the current vertex is inside the circumscribe circle of the current triangle
            # add the current triangle's edges to the candidate polygon
            if in_circle( vertex, center, radius, epsilon ):
                LOGN( "\t\t\tIn circumcircle, add to enclosing polygon",triangle )
                if do_plot:
                    # if not match_supertriangle( triangle ):
                    circ = plot.Circle(center, radius, facecolor='yellow', edgecolor="orange", alpha=0.1)
                    ax.add_patch(circ)

                for p0,p1 in tour(list(triangle)):
                    # then add this edge to the polygon enclosing the vertex
                    enclosing.append( (p0,p1) )
                # and remove the corresponding triangle from the current triangulation
                removed.append( triangle )
                completed.pop(triangle,None)

            elif do_plot:
                # if not match_supertriangle( triangle ):
                circ = plot.Circle(center, radius, facecolor='lightgrey', edgecolor="grey", alpha=0.1)
                ax.add_patch(circ)


        # end for triangle in triangles

        # The triangles in the enclosing polygon are deleted and
        # new triangles are formed between the point to be added and
        # each outside edge of the enclosing polygon. 

        # actually remove triangles
        for triangle in removed:
            # if do_plot:
                # if not match_supertriangle( triangle ):
                # uberplot.plot_segments( ax, tour(list(triangle)), edgecolor = "orange", alpha=0.3, lw=2 )

            triangles.remove(triangle)


        # remove duplicated edges
        # this leaves the edges of the enclosing polygon only,
        # because enclosing edges are only in a single triangle,
        # but edges inside the polygon are at least in two triangles.
        # duplicated = []
        # for i,ei in enumerate(enclosing):
        #     for j,ej in enumerate(enclosing,i+1):
        #         if (ei[0] == ej[1] and ei[1] == ej[0]) or (ei[0] == ej[0] and ei[1] == ej[1]):
        #             duplicated.append( ei )
        # for e in duplicated:
        #     enclosing.remove(e)
        hull = []
        for i,(p0,p1) in enumerate(enclosing):
            if (p0,p1) not in enclosing[i+1:] and (p1,p0) not in enclosing:
                hull.append((p0,p1))

        if do_plot:
            uberplot.plot_segments( ax, hull, edgecolor = "red", alpha=1, lw=1, linestyle='solid' )


        # create new triangles using the current vertex and the enclosing hull
        # All candidates should be arranged in clockwise order!
        LOGN( "\t\tCreate new triangles" )
        for p0,p1 in hull:
            assert( p0 != p1 )
            # if p0 != vertex and p1 != vertex:
            # triangle = tuple(sorted([p0,p1,vertex]))
            triangle = tuple([p0,p1,vertex])
            LOGN("\t\t\tNew triangle",triangle)
            triangles.append( triangle )
            completed[triangle] = False

            if do_plot: # linestyle = ['solid' | 'dashed' | 'dashdot' | 'dotted']
                uberplot.plot_segments( ax, tour(list(triangle)), edgecolor = "green", alpha=0.3, linestyle='solid' )


        with open("triangulation_%i.dat" % it, 'w') as fd:
            for triangle in triangles:
                for edge in tour(list(triangle)):
                    coords = tuple([coord for point in edge for coord in point])
                    fd.write( "%f %f %f %f\n" % coords )

        if do_plot:
            # ax.set_ylim([-100,200])
            # ax.set_xlim([-100,200])
            plot.savefig("triangulation_%i.png" % it, dpi=300)
            plot.close()

        it+=1

    # end for vertex in vertices


    # Remove triangles that have at least one of the supertriangle vertices
    LOGN( "\tRemove super-triangles" ) 

    # filter out elements for which the predicate is False
    # here: *keep* elements that *do not* have a common vertex
    triangulation = filter_if_not( match_supertriangle, triangles )

    return triangulation



if __name__ == "__main__":
    import random
    import utils
    import uberplot
    import matplotlib.pyplot as plot
    from matplotlib.path import Path
    import matplotlib.patches as patches

    scale = 100
    nb = 10
    points = [ (scale*random.random(),scale*random.random()) for i in range(nb)]
    # points = [
    #         (0,40),
    #         (100,60),
    #         (40,0),
    #         (50,100),
    #         (90,10),
    #         ]

    triangles = delaunay_bowyer_watson( points, epsilon=10e-4, supert=3 )

    edges = edges_of( triangles )

    fig = plot.figure()
    ax = fig.add_subplot(111)
    uberplot.scatter_segments( ax, edges, facecolor = "red" )
    uberplot.plot_segments( ax, edges, edgecolor = "blue", alpha=0.2 )
    plot.show()
