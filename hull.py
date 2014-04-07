
import operator
from utils import x,y,euclidian_distance,LOG,LOGN

# Based on the excellent article by Tom Switzer <thomas.switzer@gmail.com>
# http://tomswitzer.net/2010/12/2d-convex-hulls-chans-algorithm/

TURN_RIGHT, TURN_NONE, TURN_LEFT = (-1, 0, 1)

def turn(p, q, r):
    """Returns -1, 0, 1 if the sequence of points (p,q,r) forms a right, straight, or left turn."""
    qr = ( x(q) - x(p) ) * ( y(r) - y(p) )
    rq = ( x(r) - x(p) ) * ( y(q) - y(p) )
    # cmp(x,y) returns -1 if x<y, 0 if x==y, +1 if x>y
    return cmp( qr - rq, 0)


def keep_left(hull, point):
    """ Remove the last elements of the given hull that does not form a left turn with the given point."""

    while len(hull) > 1  and  turn( hull[-2], hull[-1], point ) != TURN_LEFT:
        hull.pop()

    # if the hull is empty or does not contains the point point
    if len(hull) == 0 or hull[-1] != point:
        # add at least the asked point
        hull.append(point)

    return hull


def graham_scan(points):
    """Returns points on convex hull of an array of points in counter clockwise order."""

    # Sort from the furthest left point.
    spots = sorted(points)

    # Browse the hull turning left from the furthest left point,
    # this is thus the lower part of the convex hull.
    lower_hull = reduce(keep_left, spots, [])

    # Going from the furthest right point, we get the upper hull.
    upper_hull = reduce(keep_left, reversed(spots), [])

    # Merge the lower and the upper hull,
    # omitting the extreme points that are in both hulls parts.
    for p in upper_hull[1:-1]:
        lower_hull.append( p )

    return lower_hull


def right_tangent(hull, p):
    """Return the index of the point in hull that the right tangent line from p to hull touches."""

    def at( index, h = hull ):
        """Secured index accessor to the hull:
        if the given index is greater than the container length, then start from the beginning."""
        return index % len(h)

    # Consider the turn formed by a window sliding
    # from the extremes points toward the center of the hull.
    #
    #                    >> sliding window <<
    #                 ___________________________
    #                /                           \
    # hull = [ . . .(. . . . . . . . . . . . . . .). . . ]
    #                ^           ^ ^ ^           ^
    #                |           | | |           |
    #                ileft       | | icenter+1   iright
    #                            | icenter
    #                            icenter-1

    # Remember that the points are ordered in the hull.
    ileft, iright = 0, len(hull)
    # With the last point.
    l_prev = turn( p, hull[0], hull[-1]            )
    # With the second point (if the hull contains only one point, then ileft stays at zero).
    l_next = turn( p, hull[0], hull[ at(ileft+1) ] )

    # While the right tangent is not found,
    # and the sliding window is not null.
    while ileft < iright:
        # Index of the point in the middle of the window.
        icenter = (ileft + iright) / 2
        # Consider the turn formed by the given point, the center point and...
        # ... the point before the center,
        c_prev = turn( p, hull[icenter], hull[ at(icenter-1) ] )
        # ... the point after the center,
        c_next = turn( p, hull[icenter], hull[ at(icenter+1) ] )
        # ... the point on the left of the window.
        c_side = turn( p, hull[ileft]  , hull[icenter]         )

        # The right tangent is the middle of the window iff
        # the turns formed with points around the center are to the LEFT (or straight)
        # (i.e. are not to the right).
        if c_prev != TURN_RIGHT and c_next != TURN_RIGHT:
            return icenter

        # If the tangent touches the left point in the window.
        elif c_side == TURN_LEFT  and ( l_next == TURN_RIGHT or l_prev == l_next ) \
          or c_side == TURN_RIGHT and   c_prev == TURN_RIGHT:
            # Do not consider points at the RIGHT of the center.
            iright = icenter

        # If the tangent touches the right point in the window,
        # but this is not the last possible tangent.
        elif icenter+1 < iright:
            # Do not consider points at the LEFT of the center.
            ileft = icenter+1
            # Switch sides: if the turn toward the point before the center
            # was to the right, search to the left and conversely.
            l_prev = -1 * c_next
            # Update the turn to the next left point.
            l_next = turn( p, hull[ileft], hull[ at(ileft+1) ] )

        # There is no more possible tangent, the hull contains a straight segment.
        else:
            return ileft

    return ileft


def min_hull_pt_pair(hulls):
    """Returns the (hull, point) index pair that is minimal."""
    # Find an extreme point and the hull chunk to which it is related.
    min_h_i, min_p_i = 0, 0
    for i,hull in enumerate(hulls):
        # Find the index j of the minimal point in the ith hull
        # itemgetter(1) will return the point, because enumerate produces (index,point) pairs
        # and thus (index,point)[1] == point
        j,pt = min(enumerate(hull), key=operator.itemgetter(1))
        # Minimize across the hulls
        if pt < hull[min_p_i]:
            min_h_i, min_p_i = i, j
    # Return the index of the hull which holds the minimal point and the index of the point itself.
    return (min_h_i, min_p_i)


def next_hull_pt_pair( hulls, (hi,pi) ):
    """ Returns the (hull, point) index pair of the next point in the convex hull."""

    # The current point itself
    base_pt = hulls[hi][pi]

    # Indices of the next (hull,point) pair in hulls
    next_hullpt = ( hi, (pi+1)%len(hulls[hi]) )

    # Now search for a "next" point after the base point
    # that forms a right turn along with its tangent point.

    # Loop over the indices of hulls,
    # but do not consider the current index.
    for nhi in (i for i in range(len(hulls)) if i != hi):
        # Index of the right tangent point of the base point
        rti = right_tangent( hulls[nhi], base_pt )

        # The other points themselves
        tangent_pt = hulls[nhi][rti]
        next_pt = hulls[ next_hullpt[0] ][ next_hullpt[1] ]

        # How is the turn formed by the three points?
        t = turn( base_pt, next_pt, tangent_pt )

        # If it forms a right turn, it is on the convex hull.
        # If it forms a left turn, it is not and we continue the loop.
        # In the (rare) case the points are aligned, we consider the next point
        # only if it is closer to the base point than the tangent point.
        if t == TURN_RIGHT \
        or ( t == TURN_NONE and euclidian_distance(base_pt, next_pt) < euclidian_distance(base_pt, tangent_pt) ):
            # save the indices of the hull and point
            next_hullpt = (nhi, rti)

    return next_hullpt


def convex_hull(points):
    """Returns the points on the convex hull of points in CCW order."""

    # Increasing guesses for the hull size.
    for guess in ( 2**(2**t) for t in range(len(points)) ):
        LOG( "Guess",guess)
        hulls = []
        for i in range(0, len(points), guess):
            # LOG(".")
            # Split the points into chunks of (roughly) the guess.
            chunk = points[i:i + guess]
            # Find the corresponding convex hull of these chunks.
            hulls.append( graham_scan(chunk) )

        # Find the extreme point and initialize the list of (hull,point) with it.
        hullpt_pairs = [min_hull_pt_pair(hulls)]

        # Ensure we stop after no more than "guess" iterations.
        for __ in range(guess):
            LOG("*")
            pair = next_hull_pt_pair(hulls, hullpt_pairs[-1])
            if pair == hullpt_pairs[0]:
                # Return the points in sequence
                LOGN("o")
                return [hulls[h][i] for h,i in hullpt_pairs]
            hullpt_pairs.append(pair)
        LOGN("x")


if __name__ == "__main__":
    import sys
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
                (50,50),
                ]

    fig = plot.figure()

    hull = convex_hull( points )
    edges = list(utils.tour(hull))

    ax = fig.add_subplot(111)
    ax.set_aspect('equal')
    ax.scatter( [i[0] for i in points],[i[1] for i in points], facecolor="red")
    uberplot.plot_segments( ax, edges, edgecolor = "blue" )
    plot.show()

