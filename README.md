Python version : Python 3.10.5
---------------------------------------------------------------------------------------

# Triangulation / Shortest path in geospatial data (.shp file)

We accept a single shapefile (.shp) containing simple polygons. There is no support
for complex polygons (with holes). The generalization of the modules (dcel.py,
dual_graph.py) to support complex polygons is possible (not even that hard) but there
is still a bug with the path finding algorithm (simple_funnel.py) so there was no time
to implement them. The bug does not break the program; it, sometimes, produces 
incorrect results (For more info on the bug see bellow). 

The program offers 5 functionalities:
1. Plot whole shapefile. (plot)
2. Find shortest path between two points. (plot)
3. Showcase user-chosen triangulation. (plot)
4. Showcase 'sleeve' path between two points. (plot)
5. Exit.

Every functionality comes with a matplotlib plot. I figured this was the only way
to showcase the results in a 'readable' way.

More specifically:
1. Plots all the polygons from the given shapefile.
2. Given two points, we plot the shortest path between them as a red sequence
   of segments along with the polygon.
3. Given a point inside a polygon, we triangulate this polygon and plot
   the triangulated polygon (all the diagonals included).
4. Given two points, we plot the sequence of triangulated faces (with their centroid
   as a red dot) that the path must cross, along with the polygon.
5. Exit.

## Running instructions

Before running the project you will need to install the requirements:
> pip install -r requirements.txt

To run the project:
> ./main.py

## Repository overview

dcel.py          : Implements a Doubly Connected Edge List (DCEL) supporting
                   needed operations and functions.

bst.py           : Minimal implementation of a BST that stores half-edges. It was 
                   created specifically for usage by the triangulation algorithm.

dual_graph.py    : Implements the Dual Graph counterpart of a DCEL. It supports only
                   triangulated DCELs.

triangulation.py : Implementation of the triangulation of a polygon. Contains all 
                   necessary functions, and also some geometric functions (ccw,
                   point_in_triangle, etc).

simple_funnel.py : Implementation of the path finding algorithm in a list of 
                   connected triangles ('sleeve' path from dual_graph.py).

test_*.py        : Unittests for all the above modules.

Every module has been tested very methodically and runs as intended (except
simple_funnel.py).

## Bug in simple_funnel.py

Given a 'sleeve' path (list of triangles) we want to find the shortest path from a point
in the leftmost triangle to a point in the rightmost triangle. This is what this module
was intended to do. I followed the logic of "simple stupid funnel algorithm"
[link](http://digestingduck.blogspot.com/2010/03/simple-stupid-funnel-algorithm.html).
What I did not notice, though, was that this algorithm fails in a specific case. This
case is when we have a big triangulated polygon and the 'sleeve' path we get has some
strange sharp turns in the middle of a relatively open field. In essence, the two 
portal vectors might get stuck! This problem was found very late, and its solution
(for an optimal algorithm) was not simple at all. Because of limited time, I overcame
this problem by making a suboptimal choice if the vectors get stuck (using the euclidean
distance as a heuristic) to unstuck the vectors. Basically, we make one of the two 
vector endpoints the new 'apex', forcefully, based on the euclidean distance of the
endpoints and the path destination point. But, there is some small chance, that this
change produces a path that crosses the polygon. I say 'there is some small chance' 
because it doesn't happen often, and I don't understand why it happens. In more detail,
we change the apex to where one of the two portal vectors points to. This should be a
totally valid choice because when a portal vector points to a point, we can safely 
assume that the path from the current 'apex' to that point is inside the polygon 
(because if it wasn't inside then the portal vector would have never pointed there).
It was very hard and time-consuming to pinpoint the case where it happens, and even
more difficult to create a unittest that fails and debug it. If I had more time
(maybe 2-3 days) I would have abandoned this module and researched for a more optimal
and reliable solution.

## Difficulties

The most difficult part of this project was making sure everything runs as intended.
The creation of solid unittests for geometric algorithms was something that I heavily
underestimated before starting this project. In any case, it was done with great care
and it took a lot of time.
