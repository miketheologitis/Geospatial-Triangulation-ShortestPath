import unittest
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from src.dcel import Dcel
from src.triangulation import (make_monotone, assign_type_to_vertices, angle_between_points_ccw,
                           triangulate_polygon, point_in_triangle)


class MyTestCase(unittest.TestCase):

    def setUp(self):
        # This is the polygon from Computational Geometry, Marc de Berg, Page 50. It is the running example
        # throughout the triangulation algorithm. (We put some arbitrary vertices that maintain the specific
        # geometry of the Book's example polygon)
        self.poly = Polygon([
            (10, 21), (11.82, 22.31), (13.48, 21.35), (14.68, 21.97),
            (14.86, 18.85), (17.2, 19.51), (16.16, 15.91), (13.88, 16.55),
            (15.58, 12.45), (10.76, 15.11), (9.58, 14.31), (8.54, 15.91),
            (9, 19), (10.38, 17.95), (10.94, 19.59)
        ])

    def test_assign_type_to_vertices(self):
        """ Minimal test checking if all vertices have been assigned a type """
        polygon_dcel = Dcel()
        polygon_dcel.build_from_polygon(self.poly)
        vertex_type = dict()
        assign_type_to_vertices(polygon_dcel, vertex_type)
        for vertex in polygon_dcel.vertices:
            self.assertIsNotNone(vertex_type[vertex])

    def test_angle_between_points_ccw(self):
        """ Thorough test for every type of angle using https://www.geogebra.org/geometry?lang=en """
        # check obtuse, acute angles
        a_list = [(3.02, 1.33), (3.02, 1.33), (3.02, 1.33), (3.02, 1.33)]
        b_list = [(6.52, 2.63), (6.52, 2.63), (6.52, 2.63), (6.52, 2.63)]
        c_list = [(4.04, 5.77), (7.52, 6.43), (2.9, 2.13), (10.18, 4.63)]
        answer = [72.1, 125.1, 12.5, 171.7]
        for a, b, c, ans in zip(a_list, b_list, c_list, answer):
            self.assertEqual(round(angle_between_points_ccw(a, b, c), 1), ans)

        # check reflex angles
        a_list = [(3.74, 1.35), (4.34, 4.01), (5.6, 4.37), (4.82, 7.99), (7.12, 8.21), (7.12, 8.21)]
        b_list = [(6.52, 2.63), (6.52, 2.63), (6.52, 2.63), (7.34, 6.49), (7.34, 6.49), (7.34, 6.49)]
        c_list = [(9.58, 1.59), (5.58, 1.05), (5.58, 1.05), (4.7, 5.01), (5.68, 1.93), (7.86, 1.95)]
        answer = [223.5, 268.4, 238.6, 300, 207.3, 180.8]
        for a, b, c, ans in zip(a_list, b_list, c_list, answer):
            self.assertEqual(round(angle_between_points_ccw(a, b, c), 1), ans)

        # check right, straight, complete angles
        a_list = [(0, 0), (0, 0), (10, 0)]
        b_list = [(8, 0), (8, 0), (8, 0)]
        c_list = [(8, 4), (12, 0), (12, 0)]
        answer = [90, 180, 0]
        for a, b, c, ans in zip(a_list, b_list, c_list, answer):
            self.assertEqual(round(angle_between_points_ccw(a, b, c), 1), ans)

    def test_make_monotone(self):
        """ Test dcel after making the Polygon monotone """
        polygon_dcel = make_monotone(self.poly)

        # Test if the 4 expected diagonals exist

        def diagonal_exists(p1, p2):
            """ Returns true if half-edge with origin p1 and its twin half-edge with origin p2 exist in DCEL """
            for hedge in polygon_dcel.hedges:
                if (hedge.origin.coordinates == p1 and hedge.twin.origin.coordinates == p2
                        or hedge.twin.origin.coordinates == p1 and hedge.origin.coordinates == p2):
                    return True
            return False

        # Diagonal 1 (v4v6 Page 50)
        v4 = (13.48, 21.35)
        v6 = (10, 21)
        self.assertTrue(diagonal_exists(v4, v6))

        # Diagonal 2 (v2v8 Page 50)
        v2 = (14.86, 18.85)
        v8 = (10.38, 17.95)
        self.assertTrue(diagonal_exists(v2, v8))

        # Diagonal 3 (v14v8 Page 50)  (v8 is defined above)
        v14 = (13.88, 16.55)
        self.assertTrue(diagonal_exists(v14, v8))

        # Diagonal 4 (v12v10 Page 50)
        v12 = (10.76, 15.11)
        v10 = (8.54, 15.91)
        self.assertTrue(diagonal_exists(v12, v10))

    def test_triangulate_polygon_only_triangles(self):
        """ Tests that for every face (excluding unbounded face) the number of half-edges bounding it, are exactly 3"""
        triangulated_dcel = triangulate_polygon(self.poly)
        for f in triangulated_dcel.faces:
            if f.outer_component is None:
                continue
            tmp_hedge = f.outer_component
            count = 0
            while True:
                tmp_hedge = tmp_hedge.next
                if tmp_hedge is f.outer_component:
                    count += 1
                    break
                count += 1
            self.assertEqual(count, 3)

    def test_triangulate_polygon_only_triangles(self):
        """ Tests that for every face (excluding unbounded face) the number of half-edges bounding it, are exactly 3"""
        triangulated_dcel = triangulate_polygon(self.poly)
        for f in triangulated_dcel.faces:
            if f.outer_component is None:
                continue
            tmp_hedge = f.outer_component
            count = 0
            while True:
                tmp_hedge = tmp_hedge.next
                if tmp_hedge is f.outer_component:
                    count += 1
                    break
                count += 1
            self.assertEqual(count, 3)

    def test_triangulate_polygon_hedges_no_none_attribute(self):
        """ Test if all edges have no None attributes """
        triangulated_dcel = triangulate_polygon(self.poly)
        for hedge in triangulated_dcel.hedges:
            self.assertIsNotNone(hedge.origin)
            self.assertIsNotNone(hedge.twin)
            self.assertIsNotNone(hedge.next)
            self.assertIsNotNone(hedge.incident_face)
            self.assertIsNotNone(hedge.prev)

    def test_triangulate_polygon_hedges_twin(self):
        """ Test in triangulated dcel twin edges """
        triangulated_dcel = triangulate_polygon(self.poly)
        for hedge in triangulated_dcel.hedges:
            self.assertIsNot(hedge, hedge.twin)
            self.assertIs(hedge, hedge.twin.twin)

    def test_triangulate_polygon_hedges_next_prev(self):
        """ For all half-edges test next/prev half-edges in the triangulated dcel """
        triangulated_dcel = triangulate_polygon(self.poly)
        for hedge in triangulated_dcel.hedges:
            self.assertIsNot(hedge, hedge.next)
            self.assertIsNot(hedge, hedge.prev)
            self.assertIs(hedge, hedge.next.prev)
            self.assertIs(hedge, hedge.prev.next)

    def test_triangulate_polygon_faces_unbounded_and_bounded(self):
        """ Test that the unbounded face exists (check if there exists a face where outer_component is None)
        and all other faces have outer_component != None
        """
        triangulated_dcel = triangulate_polygon(self.poly)
        unbounded_face = None
        for f in triangulated_dcel.faces:  # find unbounded face (also check that only 1 unbounded face exists)
            if f.outer_component is None:
                self.assertIsNone(unbounded_face)  # check that only 1 unbounded face exists
                unbounded_face = f
                self.assertTrue(unbounded_face.inner_components)  # check that inner_components is not empty
        for f in triangulated_dcel.faces:
            if f is unbounded_face:
                continue
            self.assertIsNotNone(f.outer_component)

    def test_triangulate_polygon_faces_and_hedge_incident_face_link(self):
        """ Test triangulated dcel that for each half-edge the incident_face is correctly linked (and the reverse) """
        triangulated_dcel = triangulate_polygon(self.poly)
        for f in triangulated_dcel.faces:
            if f.outer_component is None:  # we're dealing with an unbounded face
                for hedge in f.inner_components:
                    self.assertIs(hedge.incident_face, f)
                    tmp_hedge = hedge
                    while True:
                        self.assertIs(tmp_hedge.incident_face, f)
                        tmp_hedge = tmp_hedge.next
                        if tmp_hedge is hedge:
                            break
            else:  # we're dealing with an inner face
                hedge = f.outer_component
                self.assertIs(hedge.incident_face, f)
                tmp_hedge = hedge
                while True:
                    self.assertIs(tmp_hedge.incident_face, f)
                    tmp_hedge = tmp_hedge.next
                    if tmp_hedge is hedge:
                        break

    def test_point_in_triangle(self):

        self.assertTrue(point_in_triangle((2.96, 6.82), (9.2, 2.82), (-3.24, -2.54), (4.38, 3.68)))
        self.assertTrue(point_in_triangle((2.96, 6.82), (-3.24, -2.54), (9.2, 2.82), (4.38, 3.68)))
        self.assertTrue(point_in_triangle((9.2, 2.82), (2.96, 6.82), (-3.24, -2.54), (4.38, 3.68)))
        self.assertTrue(point_in_triangle((9.2, 2.82), (-3.24, -2.54), (2.96, 6.82), (4.38, 3.68)))
        self.assertTrue(point_in_triangle((-3.24, -2.54), (2.96, 6.82), (9.2, 2.82), (4.38, 3.68)))
        self.assertTrue(point_in_triangle((-3.24, -2.54), (9.2, 2.82), (2.96, 6.82), (4.38, 3.68)))

        self.assertTrue(point_in_triangle((2.96, 6.82), (9.2, 2.82), (-3.24, -2.54), (-2.04, -1.6)))
        self.assertTrue(point_in_triangle((2.96, 6.82), (-3.24, -2.54), (9.2, 2.82), (-2.04, -1.6)))
        self.assertTrue(point_in_triangle((9.2, 2.82), (2.96, 6.82), (-3.24, -2.54), (-2.04, -1.6)))
        self.assertTrue(point_in_triangle((9.2, 2.82), (-3.24, -2.54), (2.96, 6.82), (-2.04, -1.6)))
        self.assertTrue(point_in_triangle((-3.24, -2.54), (2.96, 6.82), (9.2, 2.82), (-2.04, -1.6)))
        self.assertTrue(point_in_triangle((-3.24, -2.54), (9.2, 2.82), (2.96, 6.82), (-2.04, -1.6)))

        self.assertFalse(point_in_triangle((2.96, 6.82), (9.2, 2.82), (-3.24, -2.54), (-1.64, 1.16)))
        self.assertFalse(point_in_triangle((2.96, 6.82), (-3.24, -2.54), (9.2, 2.82), (-1.64, 1.16)))
        self.assertFalse(point_in_triangle((9.2, 2.82), (2.96, 6.82), (-3.24, -2.54), (-1.64, 1.16)))
        self.assertFalse(point_in_triangle((9.2, 2.82), (-3.24, -2.54), (2.96, 6.82), (-1.64, 1.16)))
        self.assertFalse(point_in_triangle((-3.24, -2.54), (2.96, 6.82), (9.2, 2.82), (-1.64, 1.16)))
        self.assertFalse(point_in_triangle((-3.24, -2.54), (9.2, 2.82), (2.96, 6.82), (-1.64, 1.16)))

        self.assertFalse(point_in_triangle((2.96, 6.82), (9.2, 2.82), (-3.24, -2.54), (8.14, 6.56)))
        self.assertFalse(point_in_triangle((2.96, 6.82), (-3.24, -2.54), (9.2, 2.82), (8.14, 6.56)))
        self.assertFalse(point_in_triangle((9.2, 2.82), (2.96, 6.82), (-3.24, -2.54), (8.14, 6.56)))
        self.assertFalse(point_in_triangle((9.2, 2.82), (-3.24, -2.54), (2.96, 6.82), (8.14, 6.56)))
        self.assertFalse(point_in_triangle((-3.24, -2.54), (2.96, 6.82), (9.2, 2.82), (8.14, 6.56)))
        self.assertFalse(point_in_triangle((-3.24, -2.54), (9.2, 2.82), (2.96, 6.82), (8.14, 6.56)))

        self.assertFalse(point_in_triangle((2.96, 6.82), (9.2, 2.82), (-3.24, -2.54), (4.14, 0.26)))
        self.assertFalse(point_in_triangle((2.96, 6.82), (-3.24, -2.54), (9.2, 2.82), (4.14, 0.26)))
        self.assertFalse(point_in_triangle((9.2, 2.82), (2.96, 6.82), (-3.24, -2.54), (4.14, 0.26)))
        self.assertFalse(point_in_triangle((9.2, 2.82), (-3.24, -2.54), (2.96, 6.82), (4.14, 0.26)))
        self.assertFalse(point_in_triangle((-3.24, -2.54), (2.96, 6.82), (9.2, 2.82), (4.14, 0.26)))
        self.assertFalse(point_in_triangle((-3.24, -2.54), (9.2, 2.82), (2.96, 6.82), (4.14, 0.26)))

        # point lies on one of the triangle edges
        #self.assertTrue(point_in_triangle((0, 0), (10, 0), (0, 6), (0, 3)))
        #self.assertTrue(point_in_triangle((0, 0), (10, 0), (0, 6), (4, 0)))
        #self.assertTrue(point_in_triangle((0, 0), (10, 0), (0, 6), (5, 3)))

    @unittest.skip("Skip because it is a visual test with a plot and terminal output!")
    def test_assign_type_to_vertices_visual(self):
        """ Visual testing (with a plot and terminal output) for each vertex and its assigned type """
        polygon_dcel = Dcel()
        polygon_dcel.build_from_polygon(self.poly)
        vertex_type = dict()
        assign_type_to_vertices(polygon_dcel, vertex_type)
        for vertex in polygon_dcel.vertices:
            print(vertex.coordinates, vertex_type[vertex])
        x, y = self.poly.exterior.xy
        plt.plot(x, y)
        plt.show()

    @unittest.skip("It is a visual test for every polygon in one of the datasets. Was created only personal use")
    def test_triangulate_polygon_visual(self):
        def dcel_to_list_of_polygons(d):
            poly_lst = list()
            for f in d.faces:
                if f.outer_component is None:
                    continue
                h = f.outer_component
                tmp_h = h
                coord_lst = list()
                while True:
                    coord_lst.append(tmp_h.origin.coordinates)
                    tmp_h = tmp_h.next
                    if tmp_h is h:
                        break
                poly_lst.append(Polygon(coord_lst))
            return poly_lst

        triangulated_dcel = triangulate_polygon(self.poly)
        gdf = gpd.GeoDataFrame()

        i = 0
        for poly in dcel_to_list_of_polygons(triangulated_dcel):
            gdf.at[i, 'geometry'] = poly
            i += 1

        gdf.plot()
        plt.show()

    @staticmethod
    @unittest.skip("It is a visual test for every polygon in one of the datasets. Was created only personal use")
    def test_make_monotone_every_polygon_from_dataset_visual():
        """ For every polygon in the shapefile GSHHS_c_L1.shp make it monotone and plot it along with the
        corresponding y-monotone transformation."""
        def dcel_to_list_of_polygons(d):
            poly_lst = list()
            for f in d.faces:
                if f.outer_component is None:
                    continue
                h = f.outer_component
                tmp_h = h
                coord_lst = list()
                while True:
                    coord_lst.append(tmp_h.origin.coordinates)
                    tmp_h = tmp_h.next
                    if tmp_h is h:
                        break
                poly_lst.append(Polygon(coord_lst))
            return poly_lst

        shapefile = 'shapefiles\\GSHHS_shp\\c\\GSHHS_c_L1.shp'
        gdf = gpd.read_file(shapefile)

        for index, row in gdf.iterrows():
            tmp_gdf = gpd.GeoDataFrame()
            tmp_gdf['geometry'] = None

            polygon_dcel = make_monotone(row['geometry'])
            polygon_lst = dcel_to_list_of_polygons(polygon_dcel)

            i = 0
            for poly in polygon_lst:
                tmp_gdf.at[i, 'geometry'] = poly
                i += 1

            tmp_gdf.plot()
            gdf.loc[[index], 'geometry'].plot()
            plt.show()

    # Uncomment @unittest.skip for the test to run
    @staticmethod
    @unittest.skip("It is a visual test for every polygon in one of the datasets. Was created only personal use")
    def test_triangulate_every_polygon_from_dataset_visual():
        """ For every polygon in the shapefile GSHHS_c_L1.shp triangulate it and plot it along with the
        corresponding y-monotone transformation."""

        def dcel_to_list_of_polygons(d):
            poly_lst = list()
            for f in d.faces:
                if f.outer_component is None:
                    continue
                h = f.outer_component
                tmp_h = h
                coord_lst = list()
                while True:
                    coord_lst.append(tmp_h.origin.coordinates)
                    tmp_h = tmp_h.next
                    if tmp_h is h:
                        break
                poly_lst.append(Polygon(coord_lst))
            return poly_lst

        shapefile = 'shapefiles\\GSHHS_shp\\c\\GSHHS_c_L1.shp'
        gdf = gpd.read_file(shapefile)

        for index, row in gdf.iterrows():
            tmp_gdf = gpd.GeoDataFrame()
            tmp_gdf['geometry'] = None

            polygon_dcel = triangulate_polygon(row['geometry'])
            polygon_lst = dcel_to_list_of_polygons(polygon_dcel)

            i = 0
            for poly in polygon_lst:
                tmp_gdf.at[i, 'geometry'] = poly
                i += 1

            tmp_gdf.plot()
            gdf.loc[[index], 'geometry'].plot()
            plt.show()


if __name__ == '__main__':
    unittest.main()
