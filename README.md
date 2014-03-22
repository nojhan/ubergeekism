Use a turtle to draw vertex built by a Lindenmayer system, construct a penrose tiling with it, convert it to a TSP problem.

Draw a P3 penrose tiling at depth 2 and output its corresponding TSPLIB file :
python lindenmayer.py 2 > penrose3_2.tsp

Read a TSPLIB file and its optimal tour and draw them:
python tsplib.py penrose3_1.tsp penrose3_2.opt.tour

