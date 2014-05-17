Übergeekism
===========

This is an attempt at using as many as possible **cool** computer science stuff
to produce a single image.

Algorithms may not be implemented in the most efficient manner, as the aim is to
have elegant and simple code for educational purpose.

Until now, the following algorithms/data structure/concepts are used:
- the (logo) turtle,
- Lindenmayer systems,
- Penrose tiling,
- travelling salesman problem,
- ant colony algorithm,
- A\* shortest path,
- circumcircle of a triangle,
- Delaunay triangulation,
- Bowyer-Watson algorithm,
- lines and segments intersections,
- graph (adjacency list, adjacency matrix),
- hash table.

And the following ones are implemented but not used:
- convex hull,
- Chan's algorithm,

The current code is written in Python.


Penrose tiling drawing
----------------------

The main shape visible on the image is a Penrose tiling (type P3), which is a
**non-periodic tiling** with an absurd level of coolness.

The edges are **recursively** built with a **Lindenmayer system**. Yes, it is
capable of building a Penrose tiling if you know which grammar to use. Yes, this
is insanely cool.

The Lindenamyer system works by drawing edges one after another, we thus use a
(LOGO) **turtle** to draw them.

Because the L-system grammar is not very efficient to build the tiling, we
insert edges in a data structure that contains an unordered collection of unique
element: a **hash table**.


Travelling Salesman Problem
---------------------------

The Penrose tiling segments defines a **graph**, which connects a set of
vertices with a set of edges. We can consider the vertices as cities and edges
as roads between them.

Now we want to find the shortest possible route that visits each city exactly
once and returns to the origin city. This is the **Travelling Salesman
Problem**. We use an **Ant Colony Optimization** algorithm to (try) to solve it.

Because each city is not connected to every other cities, we need to find the
shortest path between two cities. This is done with the help of the famously
cool **A-star** algorithm.

The ant colony algorithm output a path that connect every cities, which is drawn
on the image, but it also stores a so-called pheromones matrix, which can be
drawn as edges with variable transparency/width.


Penrose tiling
--------------

Because the L-system draws the Penrose tiling segments by segments, we need to
compute how each segment is related to the diamonds to rebuild the tiling
corresponding to all those edges.

Fortunately, computing a **Delaunay triangulation** of the Penrose vertices
brings back  a triangular subgraph of the Penrose graph (how cool is that!?) and
stores plain shapes (triangles) instead of unordered segments. This is done
thanks to the **Bowyer-Watson algorithm**.

But this triangulation contains edges that link the set of exterior vertices,
which are not in the Penrose tiling. This is solved by ~~computing the **convex
hull**, with the **Chan's algorithm**, and removing the triangles that contains
those edges from the triangulation~~ removing obtuse triangles.


Penrose graph
-------------

We now want to connect each diamond to its neighbour, so as to build the Penrose
graph itself. One way to do that is to compute the **Voronoï diagram** of the
previous Delaunay triangulation. But we really want the Voronoï diagram of the
Penrose tiling (with diamonds), not its triangulation (with, well, triangles).

We thus need to merge each edge of the Voronoï graph that do not cross a segment
of the Penrose tiling into a single node, while preserving its neighbours. We
thus need to compute **segments intersection** (which does not seems so cool but
really is) and find a way to reduce the graph.


TODO
----

More coolness:
- **quad trees** may be useful somewhere to query neighbors points?,
- Draw the neighborhood with **splines** across the center of diamonds
  segments,
- Run a **cellular automata** on this Penrose tiling,
- Draw a **planner** on it.

Maybe even more coolness?
- percolation theory?

Improvements:
- Use a triangular matrix for pheromones in ACO.

