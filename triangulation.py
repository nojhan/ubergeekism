
import sys
import math
from itertools import ifilterfalse as filter_if_not

from utils import tour,LOG,LOGN
from geometry import mid,middle,x,y

# Based on http://paulbourke.net/papers/triangulate/
# Efficient Triangulation Algorithm Suitable for Terrain Modelling
#     An Algorithm for Interpolating Irregularly-Spaced Data
#     with Applications in Terrain Modelling
# Written by Paul Bourke
# Presented at Pan Pacific Computer Conference, Beijing, China.
# January 1989

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
    """Return True if the given point p is in the given circle"""

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


def in_triangle( p0, triangle, exclude_edges = False ):
    """Return True if the given point lies inside the given triangle"""

    p1,p2,p3 = triangle

    # Compute the barycentric coordinates
    alpha = ( (y(p2) - y(p3)) * (x(p0) - x(p3)) + (x(p3) - x(p2)) * (y(p0) - y(p3)) )   \
          / ( (y(p2) - y(p3)) * (x(p1) - x(p3)) + (x(p3) - x(p2)) * (y(p1) - y(p3)) )
    beta  = ( (y(p3) - y(p1)) * (x(p0) - x(p3)) + (x(p1) - x(p3)) * (y(p0) - y(p3)) )   \
          / ( (y(p2) - y(p3)) * (x(p1) - x(p3)) + (x(p3) - x(p2)) * (y(p1) - y(p3)) )
    gamma = 1.0 - alpha - beta
    # print alpha,beta,gamma

    if exclude_edges:
        # If all of alpha, beta, and gamma are strictly greater than 0 and lower than 1,
        # (and thus if any of them are lower or equal than 0 or greater than 1)
        # then the point p0 strictly lies within the triangle.
        return any( x <= 0 or 1 <= x for x in (alpha, beta, gamma) )
    else:
        # If the inequality is strict, then the point may lies on an edge.
        return any( x <  0 or 1 <  x for x in (alpha, beta, gamma) )


def is_acute(triangle):
    """Return True if the center of the circumcircle of the given triangle lies inside the triangle.
       That is if the triangle is acute."""
    return in_triangle( circumcircle(triangle)[0], triangle )



def bounds( vertices ):
    """Return the iso-axis rectangle enclosing the given points"""
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


def supertriangle( vertices, delta = 0.1 ):
    """Return a super-triangle that encloses all given points.
    The super-triangle has its base at the bottom and encloses the bounding box at a distance given by:
        delta*max(width,height)
    """

    # Iso-rectangle bounding box.
    (xmin,ymin),(xmax,ymax) = bounds( vertices )

    dx = xmax - xmin
    dy = ymax - ymin
    dmax = max( dx, dy )
    xmid = (xmax + xmin) / 2.0

    supertri = ( ( xmin-dy-dmax*delta, ymin-dmax*delta ),
                 ( xmax+dy+dmax*delta, ymin-dmax*delta ),
                 ( xmid              , ymax+(xmax-xmid)+dmax*delta ) )

    return supertri


def delaunay_bowyer_watson( points, supertri = None, superdelta = 0.1, epsilon = sys.float_info.epsilon,
        do_plot = None, plot_filename = "Bowyer-Watson_%i.png" ):
    """Return the Delaunay triangulation of the given points

    epsilon: used for floating point comparisons, two points are considered equals if their distance is < epsilon.
    do_plot: if not None, plot intermediate steps on this matplotlib object and save them as images named: plot_filename % i
    """

    if do_plot and len(points) > 10:
        print "WARNING it is a bad idea to plot each steps of a triangulation of many points"

    # Sort points first on the x-axis, then on the y-axis.
    vertices = sorted( points )

    # LOGN( "super-triangle",supertri )
    if not supertri:
        supertri = supertriangle( vertices, superdelta )

    # It is the first triangle of the list.
    triangles = [ supertri ]

    completed = { supertri: False }

    # The predicate returns true if at least one of the vertices
    # is also found in the supertriangle.
    def match_supertriangle( tri ):
        if tri[0] in supertri or \
           tri[1] in supertri or \
           tri[2] in supertri:
            return True

    # Returns the base of each plots, with points, current triangulation, super-triangle and bounding box.
    def plot_base(ax,vi = len(vertices), vertex = None):
        ax.set_aspect('equal')
        # regular points
        scatter_x = [ p[0] for p in vertices[:vi]]
        scatter_y = [ p[1] for p in vertices[:vi]]
        ax.scatter( scatter_x,scatter_y, s=30, marker='o', facecolor="black")
        # super-triangle vertices
        scatter_x = [ p[0] for p in list(supertri)]
        scatter_y = [ p[1] for p in list(supertri)]
        ax.scatter( scatter_x,scatter_y, s=30, marker='o', facecolor="lightgrey", edgecolor="lightgrey")
        # current vertex
        if vertex:
            ax.scatter( vertex[0],vertex[1], s=30, marker='o', facecolor="red", edgecolor="red")
        # current triangulation
        uberplot.plot_segments( ax, edges_of(triangles), edgecolor = "blue", alpha=0.5, linestyle='solid' )
        # bounding box
        (xmin,ymin),(xmax,ymax) = bounds(vertices)
        uberplot.plot_segments( ax, tour([(xmin,ymin),(xmin,ymax),(xmax,ymax),(xmax,ymin)]), edgecolor = "magenta", alpha=0.2, linestyle='dotted' )


    # Insert vertices one by one.
    LOG("Insert vertices: ")
    if do_plot:
        it=0
    for vi,vertex in enumerate(vertices):
        # LOGN( "\tvertex",vertex )
        assert( len(vertex) == 2 )

        if do_plot:
            ax = do_plot.add_subplot(111)
            plot_base(ax,vi,vertex)

        # All the triangles whose circumcircle encloses the point to be added are identified,
        # the outside edges of those triangles form an enclosing polygon.

        # Forget previous candidate polygon's edges.
        enclosing = []

        removed = []
        for triangle in triangles:
            # LOGN( "\t\ttriangle",triangle )
            assert( len(triangle) == 3 )

            # Do not consider triangles already tested.
            # If completed has a key, test it, else return False.
            if completed.get( triangle, False ):
                # LOGN( "\t\t\tAlready completed" )
                # if do_plot:
                    # uberplot.plot_segments( ax, tour(list(triangle)), edgecolor = "magenta", alpha=1, lw=1, linestyle='dotted' )
                continue

            # LOGN( "\t\t\tCircumcircle" ) 
            assert( triangle[0] != triangle[1] and triangle[1] != triangle [2] and triangle[2] != triangle[0] )
            center,radius = circumcircle( triangle, epsilon )

            # If it match Delaunay's conditions.
            if x(center) < x(vertex) and math.sqrt((x(vertex)-x(center))**2) > radius:
                # LOGN( "\t\t\tMatch Delaunay, mark as completed" ) 
                completed[triangle] = True

            # If the current vertex is inside the circumscribe circle of the current triangle,
            # add the current triangle's edges to the candidate polygon.
            if in_circle( vertex, center, radius, epsilon ):
                # LOGN( "\t\t\tIn circumcircle, add to enclosing polygon",triangle )
                if do_plot:
                    circ = plot.Circle(center, radius, facecolor='yellow', edgecolor="orange", alpha=0.2, clip_on=False)
                    ax.add_patch(circ)

                for p0,p1 in tour(list(triangle)):
                    # Then add this edge to the polygon enclosing the vertex,
                    enclosing.append( (p0,p1) )
                # and remove the corresponding triangle from the current triangulation.
                removed.append( triangle )
                completed.pop(triangle,None)

            elif do_plot:
                circ = plot.Circle(center, radius, facecolor='lightgrey', edgecolor="grey", alpha=0.2, clip_on=False)
                ax.add_patch(circ)

        # end for triangle in triangles

        # The triangles in the enclosing polygon are deleted and
        # new triangles are formed between the point to be added and
        # each outside edge of the enclosing polygon. 

        # Actually remove triangles.
        for triangle in removed:
            triangles.remove(triangle)


        # Remove duplicated edges.
        # This leaves the edges of the enclosing polygon only,
        # because enclosing edges are only in a single triangle,
        # but edges inside the polygon are at least in two triangles.
        hull = []
        for i,(p0,p1) in enumerate(enclosing):
            # Clockwise edges can only be in the remaining part of the list.
            # Search for counter-clockwise edges as well.
            if (p0,p1) not in enclosing[i+1:] and (p1,p0) not in enclosing:
                hull.append((p0,p1))
            elif do_plot:
                uberplot.plot_segments( ax, [(p0,p1)], edgecolor = "white", alpha=1, lw=1, linestyle='dotted' )



        if do_plot:
            uberplot.plot_segments( ax, hull, edgecolor = "red", alpha=1, lw=1, linestyle='solid' )


        # Create new triangles using the current vertex and the enclosing hull.
        # LOGN( "\t\tCreate new triangles" )
        for p0,p1 in hull:
            assert( p0 != p1 )
            triangle = tuple([p0,p1,vertex])
            # LOGN("\t\t\tNew triangle",triangle)
            triangles.append( triangle )
            completed[triangle] = False

            if do_plot:
                uberplot.plot_segments( ax, [(p0,vertex),(p1,vertex)], edgecolor = "green", alpha=1, linestyle='solid' )

        if do_plot:
            plot.savefig( plot_filename % it, dpi=150)
            plot.clf()

            it+=1
        LOG(".")

    # end for vertex in vertices
    LOGN(" done")


    # Remove triangles that have at least one of the supertriangle vertices.
    # LOGN( "\tRemove super-triangles" ) 

    # Filter out elements for which the predicate is False,
    # here: *keep* elements that *do not* have a common vertex.
    # The filter is a generator, so we must make a list with it to actually get the data.
    triangulation = list(filter_if_not( match_supertriangle, triangles ))

    if do_plot:
            ax = do_plot.add_subplot(111)
            plot_base(ax)
            uberplot.plot_segments( ax, edges_of(triangles), edgecolor = "red", alpha=0.5, linestyle='solid' )
            uberplot.plot_segments( ax, edges_of(triangulation), edgecolor = "blue", alpha=1, linestyle='solid' )
            plot.savefig( plot_filename % it, dpi=150)
            plot.clf()

    return triangulation


def edges_of( triangulation ):
    """Return a list containing the edges of the given list of 3-tuples of points"""
    edges = []
    for t in triangulation:
        for e in tour(list(t)):
            edges.append( e )
    return edges


def load( stream ):
    triangles = []
    for line in stream:
        if line.strip()[0] != "#":
            tri = line.strip().split()
            assert(len(tri)==3)
            triangle = []
            for p in tri:
                point = tuple(float(i) for i in p.split(","))
                assert(len(point)==2)
                triangle.append( point )
            triangles.append( triangle )
    return triangles


def write( triangles, stream ):
    for tri in triangles:
        assert(len(tri)==3)
        p,q,r = tri
        stream.write("%f,%f %f,%f %f,%f\n" % ( x(p),y(p), x(q),y(q), x(r),y(r) ) )


if __name__ == "__main__":
    import random
    import utils
    import uberplot
    import matplotlib.pyplot as plot

    if len(sys.argv) > 1:
        scale = 100
        nb = int(sys.argv[1])
        points = [ (scale*random.random(),scale*random.random()) for i in range(nb)]
    else:
        points = [
                (0,40),
                (100,60),
                (40,0),
                (50,100),
                (90,10),
                # (50,50),
                ]

    fig = plot.figure()

    triangles = delaunay_bowyer_watson( points, do_plot = fig )

    edges = edges_of( triangles )

    ax = fig.add_subplot(111)
    ax.set_aspect('equal')
    uberplot.scatter_segments( ax, edges, facecolor = "red" )
    uberplot.plot_segments( ax, edges, edgecolor = "blue" )
    plot.show()

