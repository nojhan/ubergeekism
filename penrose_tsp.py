import lindenmayer
import tsplib
import sys

depth = 1
if len(sys.argv) > 1:
    depth = int( sys.argv[1] )

segment_size = 10
float_rounding = 10

import turtle
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

penrose.draw( depth )
#print penrose

#plot_segments( penrose.segments )


tsplib.write_segments( penrose.segments, segment_size, depth, float_rounding, fd=sys.stdout )

