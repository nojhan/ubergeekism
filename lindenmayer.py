from collections import deque

class IndexedGenerator(object):
    """Add a way to get a generator item by its index"""
    def __init__(self, generator):
        self.generator = generator
        self.cache = []

    def __getitem__(self, index):
        for i in xrange( index - len(self.cache) + 1 ):
            self.cache.append( self.generator.next() )
        return self.cache[index]


class LindenmayerSystem(IndexedGenerator):
    """Base virtual class for a Lindenmayer system"""
    def __init__(self, axiom, rules, angle, heading=0):
        self.angle = angle
        self.heading = heading
        self.states = deque()
        self.actions = {
            'F': self.forward,
            '+': self.right,
            '-': self.left,
            '[': self.save,
            ']': self.restore,
        }
        super(LindenmayerSystem, self).__init__(self.lindenmayer(axiom, rules))
    
    def lindenmayer(self, axiom, rules):
        rules = rules.items()

        # def inside the lindenmayer function, so as to use "axiom" at instanciation
        def apply(axiom, (symbol, replacement)):
            return axiom.replace(symbol, replacement.lower())

        while True:
            yield axiom
            axiom = reduce(apply, rules, axiom).upper()

    def forward(self):
        raise NotImplementedError

    def right(self):
        raise NotImplementedError

    def left(self):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError

    def restore(self):
        raise NotImplementedError


class TurtleLSystem(LindenmayerSystem):
    """Draw a L-System using the Turtle module"""
    def __init__(self, turtle, axiom, rules, angle, heading=0, size=1):
        self.turtle = turtle
        self.size = size
        super(TurtleLSystem, self).__init__( axiom, rules, angle, heading )

    def draw(self, depth):        
        self.turtle.setheading(self.heading)

        for char in self[depth]:
            if char in self.actions:
                self.actions[char]()

    def forward(self):
        self.turtle.forward(self.size)

    def left(self):
        self.turtle.left(self.angle)

    def right(self):
        self.turtle.right(self.angle)

    def save(self):
        x = self.turtle.xcor()
        y = self.turtle.ycor()
        h = self.turtle.heading()
        self.states.append( (x, y, h) )

    def restore(self):
        self.turtle.up()
        x, y, h = self.states.pop()
        self.turtle.setx(x)
        self.turtle.sety(y)
        self.turtle.setheading(h)
        self.turtle.down()


class DumpTurtleLSystem(TurtleLSystem):
    """Keep the set of uniques L-System segments drawn by the Turtle"""
    def __init__(self, turtle, axiom, rules, angle, heading=0, size=1, rounding=10):
        # using a set avoid duplicate segments
        self.segments = set()
        # nb of significant digits for rounding
        self.rounding=10
        super(DumpTurtleLSystem, self).__init__( turtle, axiom, rules, angle, heading, size )

    def forward(self):
        """Store segment coordinates and do a forward movement"""
        # without rounding, there may be the same node with different coordinates, 
        # because of error propagation
        x1 = round( self.turtle.xcor(), self.rounding )
        y1 = round( self.turtle.ycor(), self.rounding )
        start = ( x1, y1 )
        super(DumpTurtleLSystem, self).forward()
        x2 = round( self.turtle.xcor(), self.rounding )
        y2 = round( self.turtle.ycor(), self.rounding )
        end = ( x2, y2 )
        self.segments.add( (start,end) )

    def draw(self, depth):
        """Call the draw function, then clean the data"""
        super(DumpTurtleLSystem, self).draw(depth)
        self.clean()

    def clean(self):
        """Remove segments that have duplicated clones in the reverse direction 
           (the segments is a set, that guarantees that no other clone exists)"""
        for segment in self.segments:
            for start,end in segment:
                # FIXME surely faster to catch the exception than to do two search?
                if (end,start) in self.segments:
                    self.segments.remove( (end,start) )

    def __str__(self):
        dump = ""
        for segment in self.segments:
            for coords in segment:
                for x in coords:
                    dump += str(x)+" "
            dump += "\n"
        return dump


def plot_segments( segments ):

    import matplotlib.pyplot as plot
    from matplotlib.path import Path
    import matplotlib.patches as patches
    
    fig = plot.figure()
    ax = fig.add_subplot(111)

    for segment in segments:
        start,end = segment
        verts = [start,end,(0,0)]
        codes = [Path.MOVETO,Path.LINETO,Path.STOP]
        path = Path(verts, codes)
        patch = patches.PathPatch(path, facecolor='none', lw=1)
        ax.add_patch(patch)

    ax.set_xlim(-50,50)
    ax.set_ylim(-50,50)

    plot.show()



if __name__=="__main__":
    import sys

    depth = 1
    if len(sys.argv) > 1:
        depth = int( sys.argv[1] )

    segment_size = 10
    float_rounding = 10

    import turtle
    ttl = turtle.Turtle()
    ttl.speed('fastest')
    penrose = DumpTurtleLSystem(ttl, 
            axiom="[X]++[X]++[X]++[X]++[X]", 
            rules={
                'F': "",
                'W': "YF++ZF----XF[-YF----WF]++",
                'X': "+YF--ZF[---WF--XF]+",
                'Y': "-WF++XF[+++YF++ZF]-",
                'Z': "--YF++++WF[+ZF++++XF]--XF"
            }, 
            angle=36, heading=0, size=segment_size, rounding=float_rounding )

    penrose.draw( depth )
    print penrose

    plot_segments( penrose.segments )

