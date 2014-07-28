#!/usr/bin/env python

import geometry
from geometry import x,y

# import enum

class QuadTree(object):

    def __init__( self, points = [] ):
        """Build a quadtree on the given set of points."""

        # Initialize the root quadrant as the box around the points
        self.init( points = points )

        # Data structures to handle the quadtree
        self.residents = { self.root: None }

        # Quadrants may have four children
        self.children = { self.root: [] }

        # Status of quadrants
        # class Status(enum.Enum):
        class Status:
            Leaf = 1
            Node = 2
            Empty = 3
            Out = 4
        self.Status = Status()

        self.walk = self.iterative_walk

        self.build(points)


    def init( self, quadrant = None, box = None, points = None ):
        """Initialize the root quadrant with the given quadrant ((x,y),width), the given box or the given set of points."""

        if len([k for k in (box,points,quadrant) if k]) > 1:
            raise BaseException("ERROR: you should specify only one of the options")

        # Initialize the root quadrant as the given box
        if box:
            minp,maxp = box
            width = max( x(maxp)-x(minp), y(maxp)-y(minp) )

        # Initialize the root quadrant as the box around the points
        elif points:
            minp,maxp = geometry.box( points )
            width = max( x(maxp)-x(minp), y(maxp)-y(minp) )

        # Initialize the root quadrant as the given origin point and width
        elif quadrant:
            minp = quadrant[0]
            width = quadrant[1]

        else:
            raise BaseException("ERROR: you should specify a box, a quadrant or points")

        # There is always the root quadrant in the list of available ones.
        self.root = (minp,width)
        self.quadrants = [ self.root ]


    def as_box( self, quadrant );
        width = quadrant[1]
        maxp = tuple(xy+width for xy in quadrant[0])
        return (quadrant[0],maxp)


    def status( self, point, quadrant ):
        """Return Status.Empty if the given point can be appended in the given quadrant."""

        assert(point is not None)
        assert(len(point) == 2)
        assert(quadrant is not None)
        assert(len(quadrant) == 2)

        box = self.as_box( quadrant )

        # if the point lies inside the given quadrant
        if geometry.in_box( point, box):
            if self.residents[quadrant]:
                # external: a quadrant that already contains a point
                assert( not self.children[quadrant] )
                # print("is external leaf")
                return self.Status.Leaf
            elif self.children[quadrant]:
                # internal: a quadrant that contains other quadrants
                return self.Status.Node
            else:
                # empty: there is not point yet in this quadrant
                return self.Status.Empty
        else:
            # point is out of the quadrant
            return self.Status.Out


    def split(self, quadrant ):
        """Split an existing quadrant in four children quadrants.

        Spread existing residents to the children."""

        # We cannot split a quadrant if it already have sub-quadrants
        if quadrant != self.root:
            assert( not self.children[quadrant] )

        qx, qy = quadrant[0]
        w = quadrant[1] / 2

        # For each four children quadrant's origins
        self.children[quadrant] = []
        for orig in ((qx,qy), (qx,qy+w), (qx+w,qy+w), (qx+w,qy)):
            q = (orig,w)
            # Create a child quadrant of half its width
            self.quadrants.append(q)
            self.residents[q] = None

            # Add a new child to the current parent.
            self.children[quadrant].append(q)
            # The new quadrant has no child.
            self.children[q] = []

        assert( len(self.children[quadrant]) == 4 )

        # Move the resident to the related children node
        p = self.residents[quadrant]
        if p is not None:
            # Find the suitable children quadrant
            for child in self.children[quadrant]:
                if self.status(p,child) == self.Status.Empty:
                    self.residents[child] = p
                    break
            # Forget we had resident here
            # Do not pop the key, because we have tests on it elsewhere
            self.residents[quadrant] = None



    def append( self, point, quadrant = None ):
        """Try to inset the given point in the existing quadtree, under the given quadrant.

        The default quadrant is the root one.
        Returns True if the point was appended, False if it is impossible to append it."""

        # Default to the root quadrant
        if not quadrant:
            quadrant = self.root
        assert(quadrant in self.quadrants)

        # The point should not be out of the root quadrant
        assert( self.status(point,self.root) != self.Status.Out )

        for q in self.walk(quadrant):
            status = self.status( point, q )
            if status == self.Status.Leaf:
                # Create sub-quadrants
                self.split(q)
                # Try to attach the point in children quadrants, recursively
                for child in self.children[q]:
                    if self.append( point, child ):
                        return True
            elif status == self.Status.Empty:
                # add the point as an resident of the quadrant q
                self.residents[q] = point
                return True
        return False


    def build(self, points):
        """append all the given points in the quadtree."""
        for p in points:
            self.append(p)
        assert( len(points) == len(self) )


    def iterative_walk(self, at_quad = None ):

        # Default to the root quadrant
        if not at_quad:
            at_quad = self.root

        # First, consider the root quadrant
        yield at_quad

        # then children of the root quadrant
        quads = list(self.children[at_quad])
        for child in quads:
            yield child
            # then children of the current child
            quads.extend( self.children[child] )


    def recursive_walk(self, at_quad = None ):

        # Default to the root quadrant
        if not at_quad:
            at_quad = self.root

        yield at_quad
        for child in self.children[at_quad]:
            for q in self.recursive_walk(child):
                yield q


    def repr(self, quad=None, depth=0):

        # Default to the root quadrant
        if not quad:
            quad = self.root

        head = "  "*depth
        r = head+"{"
        quadrep = '"origin" : %s, "width" : %f' % quad
        if self.residents[quad]: # external
            r += ' "resident" : %s, \t%s },\n' % (self.residents[quad],quadrep)
        elif self.children[quad]: # internal
            r += ' "children_ids" : %s, \t%s, "children" : [\n' % (self.children[quad],quadrep)
            for child in self.children[quad]:
                r += self.repr(child, depth+1)
            r+="%s]},\n" % head
        else: # empty
            r += ' "resident" : (), \t\t\t%s},\n' % (quadrep)
        return r


    def points( self ):
        return [p for p in self.residents.values() if p is not None]


    def __iter__(self):
        return iter(self.points())


    def __call__(self, points):
        self.build(points)


    def __len__(self):
        """Return the number of points attached to the quad tree."""
        return len(self.points())


    def __repr__(self):
        return self.repr()


if __name__ == "__main__":

    import sys
    import math
    import random

    import utils
    import uberplot
    import matplotlib.pyplot as plot

    if len(sys.argv) == 2:
        seed = sys.argv[1]
    else:
        seed = None

    random.seed(seed)

    n=20
    points = [ ( round(random.uniform(-n,n),2),round(random.uniform(-n,n),2) ) for i in range(n) ]

    quad = QuadTree( points )
    print(quad)
    sys.stderr.write( "%i points in the quadtree / %i points\n" % (len(quad), len(points)) )


    fig = plot.figure()

    ax = fig.add_subplot(111)
    ax.set_aspect('equal')
    uberplot.scatter_points( ax, points, facecolor="red", edgecolor="red")
    # uberplot.scatter_points( ax, quad.points(), facecolor="green", edgecolor="None")
    uberplot.scatter_points( ax, list(quad), facecolor="green", edgecolor="None")

    for q in quad.quadrants:
        qx, qy = q[0]
        w = q[1]
        box = [(qx,qy), (qx,qy+w), (qx+w,qy+w), (qx+w,qy)]
        edges = list( utils.tour(box) )
        uberplot.plot_segments( ax, edges, edgecolor = "blue", alpha = 0.1, linewidth = 2 )


    plot.show()

    assert(len(points) == len(quad))

