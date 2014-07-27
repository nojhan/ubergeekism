
# import enum

import geometry
from geometry import x,y

def next_id( existing_ids ):
    i = 0
    while i in existing_ids:
        i += 1
    return i


class QuadTree(object):

    def __init__( self, points = [] ):

        # Data structures to handle the quadtree

        # 0 is the root quadrant
        self.quadrants = { 0: None }
        self.widths = { 0: None }
        self.occupants = { 0: None }
        # Quadrants may have four children
        self.children = { 0: [] }

        # Initialize the root quadrant as the box around the points
        self.init(points = points)

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
        if len([k for k in (box,points,quadrant) if k]) > 1:
            raise BaseException("ERROR: you should specify only one of the options")

        # Initialize the root quadrant as the box around the points
        if box:
            minp,maxp = box
            w = max( x(maxp)-x(minp), y(maxp)-y(minp) )
            self.widths[0] = w
            self.quadrants[0] = minp
        elif points:
            minp,maxp = geometry.box( points )
            w = max( x(maxp)-x(minp), y(maxp)-y(minp) )
            self.widths[0] = w
            self.quadrants[0] = minp
        elif quadrant:
            self.quadrants[0] = quadrant[0]
            self.widths[0] = quadrant[1]
        else:
            raise BaseException("ERROR: you should specify a box, a quadrant or points")


    def appendable( self, p, quad ):
        """Return Status.Empty if the given point can be appended in the given quadrant."""
        assert(p is not None)
        assert(len(p) == 2)
        minp = self.quadrants[quad]
        assert(minp is not None)
        assert(len(minp) == 2)
        w = self.widths[quad]
        maxp = tuple(i+w for i in minp)
        box = (minp,maxp)

        # if the point lies inside the given quadrant
        if geometry.in_box( p, box):
            if self.occupants[quad]:
                # external: a quadrant that already contains a point
                assert( not self.children[quad] )
                # print("is external leaf")
                return self.Status.Leaf
            elif self.children[quad]:
                # internal: a quadrant that contains other quadrants
                # print("is internal node")
                return self.Status.Node
            else:
                # empty: there is not point yet in this quadrant
                # print("is empty")
                return self.Status.Empty
        else:
            # point is out of the quadrant
            # print("is out")
            return self.Status.Out


    def split(self, quadrant ):
        """Split an existing quadrant in four children quadrants.

        Spread existing occupants to the children."""

        # We cannot split a quadrant if it already have sub-quadrants
        if quadrant != 0:
            assert( not self.children[quadrant] )

        qx, qy = self.quadrants[quadrant]
        w = self.widths[quadrant] / 2

        # For each four children quadrant's origins
        for orig in ((qx,qy), (qx,qy+w), (qx+w,qy+w), (qx+w,qy)):
            # Create a child quadrant of half its width
            id = next_id( self.quadrants )
            self.widths[id] = w
            self.quadrants[id] = orig
            self.occupants[id] = None

            # add a new child to the current parent
            self.children[quadrant].append(id)
            self.children[id] = []

        # Move the occupant to the related children node
        p = self.occupants[quadrant]
        if p is not None:
            # Find the suitable children quadrant
            for child in self.children[quadrant]:
                if self.appendable(p,child) == self.Status.Empty:
                    self.occupants[child] = p
                    break
            # Forget we had occupant here
            # Do not pop the key, because we have tests on it elsewhere
            self.occupants[quadrant] = None

        assert( len(self.children[quadrant]) == 4 )


    def append( self, point, quadrant = 0 ):
        """Try to inset the given point in the existing quadtree, under the given quadrant.

        The default quadrant is the root one (0).
        Returns True if the point was appended, False if it is impossible to append it."""
        assert(quadrant in self.quadrants)
        # The point should not be out the root quadrant
        assert( self.appendable(point,0) != self.Status.Out )

        for q in self.walk(quadrant):
            status = self.appendable( point, q )
            if status == self.Status.Leaf:
                # Create sub-quadrants
                self.split(q)
                # Try to attach the point in children quadrants, recursively
                for child in self.children[q]:
                    # print("consider children %i" % child)
                    if self.append( point, child ):
                        return True
            elif status == self.Status.Empty:
                # add the point as an occupant of the quadrant q
                self.occupants[q] = point
                # print("%s appended at %i" % (point,q))
                return True
        return False


    def build(self, points):
        """append all the given points in the quadtree."""
        for p in points:
            self.append(p)
        # assert( len(points) == len(self) )


    def iterative_walk(self, at_quad = 0 ):
        # First, consider the root quadrant
        yield at_quad

        # then children of the root quadrant
        quads = list(self.children[at_quad])
        for child in quads:
            yield child
            # then children of the current child
            quads.extend( self.children[child] )


    def recursive_walk(self, at_quad = 0 ):
        yield at_quad
        for child in self.children[at_quad]:
            for q in self.recursive_walk(child):
                yield q


    def repr(self,quad=0,depth=0):
        head = "  "*depth
        r = head+"{"
        quadrep = '"origin" : %s, "width" : %f' % (self.quadrants[quad],self.widths[quad])
        if self.occupants[quad]: # external
            r += ' "id" : %i, "occupant" : %s, \t%s },\n' % (quad,self.occupants[quad],quadrep)
        elif self.children[quad]: # internal
            r += ' "id" : %i, "children_ids" : %s, \t%s, "children" : [\n' % (quad,self.children[quad],quadrep)
            for child in self.children[quad]:
                r += self.repr(child, depth+1)
            r+="%s]},\n" % head
        else: # empty
            r += ' "id" : %i, "occupant" : (), \t\t\t%s},\n' % (quad,quadrep)
        return r


    def points( self ):
        # return [self.occupants[q] for q in self.occupants if self.occupants[q] is not None]
        return [p for p in self.occupants.values() if p is not None]


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

    n=200
    points = [ ( round(random.uniform(-n,n),2),round(random.uniform(-n,n),2) ) for i in range(n) ]

    quad = QuadTree( points )
    print(quad)
    sys.stderr.write( "%i attached points / %i appended points\n" % (len(quad), len(points)) )


    fig = plot.figure()

    ax = fig.add_subplot(111)
    ax.set_aspect('equal')
    uberplot.scatter_points( ax, points, facecolor="red", edgecolor="red")
    uberplot.scatter_points( ax, quad.points(), facecolor="green", edgecolor="None")

    for q in quad.quadrants:
        qx, qy = quad.quadrants[q]
        w = quad.widths[q]
        box = [(qx,qy), (qx,qy+w), (qx+w,qy+w), (qx+w,qy)]
        edges = list( utils.tour(box) )
        uberplot.plot_segments( ax, edges, edgecolor = "blue", alpha = 0.1, linewidth = 2 )


    plot.show()

    assert(len(points) == len(quad))

