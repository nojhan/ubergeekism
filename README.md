Übergeekism
===========

This is an attempt at using as many as possible *cool* computer science stuff to produce a single image.

Algorithms may not be implemented in the most efficient manner, as the aim is to have elegant and simple code for
educationnal purpose.

Until now, the following algorithms/data structure/concepts are used:
- the (logo) turtle,
- Lindenmayer systems,
- Penrose tiling,
- Travelling salesman problem,
- ant colony algorithm,
- A-star shortest path,
- graph (adjacency list, adjacency matrix),
- hash table.

The current code is written in Python.


Penrose tiling
--------------

The main shape visible on the image is a Penrose tiling (type P3), which is a *non-periodic tiling* with an absurd level
of coolness.

The edges are *recursively* built with a *Lindenmayer system*. Yes, it is capable of building a Penrose tiling if you
know which grammar to use. Yes, this is insanely cool.

The Lindenamyer system works by drawing edges one after another, we thus use a (LOGO) *turtle* to draw them.

Because the L-system grammar is not very efficient to build the tiling, we insert edges in a data structure that
contains an unordered collection of unique element: a *hash table*.


Travelling Salesman Problem
---------------------------

The Penrose tiling defines a *graph*, which connects a set of vertices with a set of edges. We can consider the vertices
as cities and edges as roads between them.

Now we want to find the shortest possible route that visits each city exactly once and returns to the origin city. This
is the *Travelling Salesman Problem*. We use an *Ant Colony Optimization* algorithm to (try) to solve it.

Because each city is not connected to every other cities, we need to find the shortest path between two cities. This is
done with the help of the *A-star* algorithm.

The ant colony algorithm output a path that connect every cities, which is drawn on the image, but it also stores a
so-called pheromones matrix, which can be drawn as edges with variable transparency/width.


TODO
----

More coolness:
- Compute the *Delaunay triangulation* from the Penrose graph vertices,
- Compute the *Voronoï diagram* (Bowyer-Watson or Fortune's algorithm?) from the triangulation,
- Remove Voronoï edges that intersects with the Penrose graph,
- *quad trees* may be useful somewhere to query neighbors points?,
- The center of remaining segments is the center of the Penrose tiles,
- Build back the neighborhood of those tiles from the Voronoï diagram,
- Run a *cellular automata* on this Penrose tiling,
- Draw a *planner* on it.

Maybe even more coolness?
- percolation theory?

Improvements:
- Use a triangular matrix for pheromones in ACO.

