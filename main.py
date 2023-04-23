import geopandas as gpd
from shapely.geometry import Polygon, Point, LineString
from src.triangulation import triangulate_polygon, find_triangle_face_containing_point
from src.dual_graph import DualGraph
from src.simple_funnel import funnel_shortest_path
import matplotlib.pyplot as plt

from pathlib import Path
import os


def face_to_coordinates(face):
    points = []
    hedge = face.outer_component
    while True:
        points.append(hedge.origin.coordinates)
        hedge = hedge.next
        if hedge is face.outer_component:
            break
    return points


def faces_to_geo_data_frame(faces):
    return gpd.GeoDataFrame(
        geometry=[
            Polygon(face_to_coordinates(f)) for f in faces if f.outer_component is not None
        ]
    )


def faces_to_centroid_points_geo_data_frame(faces):
    return gpd.GeoDataFrame(
        geometry=[
            Polygon(face_to_coordinates(f)).centroid for f in faces if f.outer_component is not None
        ]
    )


def menu():
    print("\nChoose number from 1-5")
    print("1. Plot whole shapefile. (plot)")
    print("2. Find shortest path between two points."
          " (In some cases path is sub-optimal. See README for more info). (plot)")
    print("3. Showcase user-chosen triangulation. (plot)")
    print("4. Showcase 'sleeve' path between two points. (plot)")
    print("5. Exit.")


if __name__ == '__main__':

    #shape_file = "../data/shapefiles/GSHHS_shp/c/GSHHS_c_L1.shp"

    shape_file = input("\nShapefile path (.shp file): ")

    poly_dcel_dict = dict()

    df = gpd.read_file(shape_file)

    while True:
        menu()
        choice = int(input("\nEnter your Choice: "))

        if choice == 1:
            print("\n*** Plotting ***")
            df.plot()
            print("*** Finished Plotting ***")
            plt.show()

        elif choice == 2:
            found = False

            start = tuple(map(float, input("\nEnter starting point as \"x, y\": ").split(',')))
            dest = tuple(map(float, input("Enter destination point as \"x, y\": ").split(',')))

            for index, row in df.iterrows():
                if row['geometry'].contains(Point(start)) and row['geometry'].contains(Point(dest)):
                    found = True

                    print("\n*** Triangulation ***")
                    if index in poly_dcel_dict:  # if we computed a triangulation of this polygon earlier
                        triangulated_dcel = poly_dcel_dict[index]
                    else:  # Triangulate the polygon
                        triangulated_dcel = triangulate_polygon(row['geometry'])  # Triangulation
                        poly_dcel_dict[index] = triangulated_dcel  # Store it for (maybe) later use
                    print("*** Finished Triangulation ***")

                    print("*** Dual Graph Creation ***")
                    # Find face containing starting point and build DualGraph with it as root
                    f = find_triangle_face_containing_point(triangulated_dcel, start)  # face containing start point
                    dual_graph = DualGraph(triangulated_dcel, f)
                    print("*** Finished Dual Graph Creation ***")

                    print("*** Finding 'sleeve' path in Dual Graph ***")
                    # Find 'sleeve' path
                    faces_path = dual_graph.path_to_point(dest)
                    print("*** Finished finding 'sleeve' path in Dual Graph ***")

                    print("*** Finding shortest path ***")
                    # Find the (sometimes suboptimal) shortest path from start to dest
                    line_string = funnel_shortest_path(faces_path, start, dest, row['geometry'])
                    print("*** Finished finding shortest path ***")

                    print("*** Plotting ***")
                    # Plot polygon containing points and shortest path
                    fig, ax = plt.subplots()
                    ax.set_aspect('equal')
                    gpd.GeoSeries(row['geometry']).plot(ax=ax)
                    gpd.GeoSeries(LineString(line_string)).plot(ax=ax, color='red')
                    print("*** Finished plotting ***")
                    plt.show()

                    break
            if not found:
                print("\nPoints may exist in different Polygons or are invalid! ")

        elif choice == 3:
            found = False

            point = tuple(
                map(
                    float,
                    input("\nEnter a point that lies in a polygon you want to triangulate as \"x, y\": ").split(',')
                )
            )

            for index, row in df.iterrows():
                if row['geometry'].contains(Point(point)):
                    found = True

                    print("*** Triangulation ***")
                    if index in poly_dcel_dict:  # if we computed a triangulation of this polygon earlier
                        triangulated_dcel = poly_dcel_dict[index]
                    else:
                        triangulated_dcel = triangulate_polygon(row['geometry'])  # Triangulation
                        poly_dcel_dict[index] = triangulated_dcel  # Store it for (maybe) later use
                    print("*** Finished Triangulation ***")

                    print("*** Plotting ***")
                    # Convert all triangular faces in triangulated_dcel to a GeoDataFrame, and plot
                    faces_to_geo_data_frame(triangulated_dcel.faces).plot()
                    plt.show()
                    print("*** Finished plotting ***")
                    break
            if not found:
                print("\nPoint does not lie inside a Polygon! ")

        elif choice == 4:
            found = False

            start = tuple(map(float, input("\nEnter starting point as \"x, y\": ").split(',')))
            dest = tuple(map(float, input("Enter destination point as \"x, y\": ").split(',')))

            for index, row in df.iterrows():
                if row['geometry'].contains(Point(start)) and row['geometry'].contains(Point(dest)):
                    found = True

                    print("\n*** Triangulation ***")
                    if index in poly_dcel_dict:  # if we computed a triangulation of this polygon earlier
                        triangulated_dcel = poly_dcel_dict[index]
                    else:  # Triangulate the polygon
                        triangulated_dcel = triangulate_polygon(row['geometry'])  # Triangulation
                        poly_dcel_dict[index] = triangulated_dcel  # Store it for (maybe) later use
                    print("*** Finished Triangulation ***")

                    print("*** Dual Graph Creation ***")
                    # Find face containing starting point and build DualGraph with it as root
                    f = find_triangle_face_containing_point(triangulated_dcel, start)  # face containing start point
                    dual_graph = DualGraph(triangulated_dcel, f)
                    print("*** Finished Dual Graph Creation ***")

                    print("*** Finding 'sleeve' path in Dual Graph ***")
                    # Find 'sleeve' path
                    faces_path = dual_graph.path_to_point(dest)
                    print("*** Finished finding 'sleeve' path in Dual Graph ***")

                    print("*** Plotting ***")
                    # Plot polygon containing points and 'sleeve' path
                    fig, ax = plt.subplots()
                    ax.set_aspect('equal')
                    gpd.GeoSeries(row['geometry']).plot(ax=ax)
                    faces_to_geo_data_frame(faces_path).plot(ax=ax, edgecolor='black', linewidth=0.2)
                    faces_to_centroid_points_geo_data_frame(faces_path).plot(ax=ax, color='red', markersize=1)
                    print("*** Finished plotting ***")
                    plt.show()
                    #21.6, -20.5   -7.2, 31.4
                    break
            if not found:
                print("\nPoints may exist in different Polygons or are invalid! ")

        elif choice == 5:
            break



