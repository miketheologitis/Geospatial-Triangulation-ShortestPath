Python version : Python 3.10.10
---------------------------------------------------------------------------------------

# Geospatial-Triangulation-ShortestPath

This project provides a set of tools for processing geospatial data in the form of shapefiles (.shp) containing simple polygons. The primary functionalities include triangulation, shortest path calculation, and visualization of geospatial data.

## Features

1. Plot the entire shapefile.
2. Find and plot the shortest path between two points.
3. Showcase user-chosen triangulations.
4. Showcase 'sleeve' paths between two points.
5. Exit.

## Project Structure

The repository is organized as follows:

| - Geospatial-Triangulation-ShortestPath
  | - __init__.py
  | - unit_tests
      | - __init__.py
      | - test_bst.py
      | - test_dcel.py
      | - test_dual_graph.py
      | - test_simple_funnel.py
      | - test_triangulation.py
  | - src
      | - __init__.py
      | - bst.py
      | - dcel.py
      | - dual_graph.py
      | - simple_funnel.py
      | - triangulation.py
  | - data
      | - shapefiles
	    | - ...
		| - README.txt
  | - main.py
  | - conda_requirements.txt
  | - pip_requirements.txt
  | - README.md
  
### `src` directory

- `bst.py`: A minimal implementation of a Binary Search Tree (BST) that stores half-edges, designed for use by the triangulation algorithm.
- `dcel.py`: Implements a Doubly Connected Edge List (DCEL) supporting necessary operations and functions.
- `dual_graph.py`: Implements the Dual Graph counterpart of a DCEL, supporting only triangulated DCELs.
- `simple_funnel.py`: Implements a pathfinding algorithm for a list of connected triangles ('sleeve' path from `dual_graph.py`).
- `triangulation.py`: Contains the implementation of the triangulation of a polygon, along with necessary functions and geometric operations.

### `unit_tests` directory

- `test_bst.py`: Unit tests for the `bst.py` module.
- `test_dcel.py`: Unit tests for the `dcel.py` module.
- `test_dual_graph.py`: Unit tests for the `dual_graph.py` module.
- `test_simple_funnel.py`: Unit tests for the `simple_funnel.py` module.
- `test_triangulation.py`: Unit tests for the `triangulation.py` module.

### `data` directory

Many different `.shp` files. Refer to the `shapefiles/README.txt`

## Installation

To install the required dependencies using `pip`, run:

```bash
pip install -r requirements.txt
```

To install the required dependecies using `conda`, run:

```bash
conda create --name new_geo_env --file conda_requirements.txt
```

## Running instructions

To run the project:
```bash
python -m main
```

## Known Issues
There is a known bug in the `simple_funnel.py` module, which may produce incorrect results in certain cases.
For more information, please refer to the comments in the module's source code (this is due to the incorrect 
idea from [link](http://digestingduck.blogspot.com/2010/03/simple-stupid-funnel-algorithm.html))
