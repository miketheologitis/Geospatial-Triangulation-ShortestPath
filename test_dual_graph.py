import unittest
from triangulation import triangulate_polygon, triangle_face_contains_point
from shapely.geometry import Polygon, Point
from dual_graph import DualGraph
from random import uniform


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.poly = Polygon([
            (10, 21), (11.82, 22.31), (13.48, 21.35), (14.68, 21.97),
            (14.86, 18.85), (17.2, 19.51), (16.16, 15.91), (13.88, 16.55),
            (15.58, 12.45), (10.76, 15.11), (9.58, 14.31), (8.54, 15.91),
            (9, 19), (10.38, 17.95), (10.94, 19.59)
        ])
        self.triangulated_dcel = triangulate_polygon(self.poly)

        # Create all possible dual graphs (starting from all faces except the unbounded one) and store them in a dual
        # graph list
        self.dg_list = [DualGraph(self.triangulated_dcel, f) for f in self.triangulated_dcel.faces
                        if f.outer_component is not None]

        # Find unbounded face which will help us in the tests (Remember that our Dual Graph does not contain it)
        self.unbounded_face = [f for f in self.triangulated_dcel.faces if f.outer_component is None][0]

    def test_create_dual_graph(self):
        """ For each dual graph in the list of dual graphs, traverse all nodes and test that each face of the
        triangulated DCEL exists in only one node in the Dual Graph. Also test that the discovered faces in the
        dual graph are exactly the faces in triangulated_dcel.faces (without the unbounded face) """

        visited_faces = set()  # Set with all the faces (or, else, nodes) we have discovered

        def traverse(node):
            self.assertNotIn(node.face, visited_faces)  # we just discovered this face, so it must not be in
            visited_faces.add(node.face)  # Add it
            for child in node.children:
                traverse(child)

        for dg in self.dg_list:  # Test for every dual graph
            traverse(dg.root)
            # Test that the faces we discovered are exactly the faces in the triangulated DCEL.
            # Note: we must add the unbounded face because it doesn't exist in the Dual graph
            self.assertNotIn(self.unbounded_face, visited_faces)  # Check unbounded face is indeed not in Dual Graph
            visited_faces.add(self.unbounded_face)  # Add unbounded face so we check equality
            self.assertSetEqual(visited_faces, self.triangulated_dcel.faces)
            visited_faces.clear()

    def test_find_node_containing_point(self):
        """ Tests that whenever point lies inside some face of the Dual Graph, we find a node containing it (face) """
        for dg in self.dg_list:
            rand_x = uniform(2, 30)  # polygon x-coordinates lie in [8.5, 17.2]
            rand_y = uniform(5, 30)  # polygon y-coordinates lie in [12.5, 22.3]
            for _ in range(1000):
                dg.find_node_containing_point(dg.root, (rand_x, rand_y))
                if self.poly.contains(Point(rand_x, rand_y)):  # from shapely library
                    self.assertIsNotNone(dg.target_node)
                else:
                    self.assertIsNone(dg.target_node)
                dg.target_node = None

    def test_path_to_point(self):
        """ Tests that whenever point lies inside some face of the Dual Graph, we find non-empty path of faces.
         Also test that the last face in the path always contains the point. """
        for dg in self.dg_list:
            rand_x = uniform(8.5, 17.2)  # polygon x-coordinates lie in [8.5, 17.2]
            rand_y = uniform(12.5, 22.3)  # polygon y-coordinates lie in [12.5, 22.3]
            for _ in range(1000):
                path = dg.path_to_point((rand_x, rand_y))
                if self.poly.contains(Point(rand_x, rand_y)):  # from shapely library
                    self.assertTrue(path)  # not empty
                    self.assertTrue(triangle_face_contains_point(path[-1], (rand_x, rand_y)))
                else:
                    self.assertFalse(path)  # empty

    def test_root_face(self):
        """ Find the face of triangulated_dcel that contains the point (13, 19) and create the DualGraph from this face.
        Test afterwards, that root.face is indeed this face, and that it also contains the point (13, 19)"""
        for f in self.triangulated_dcel.faces:
            if f is self.unbounded_face:
                continue
            if triangle_face_contains_point(f, (13, 19)):
                face_of_point = f
                break
        dg = DualGraph(self.triangulated_dcel, face_of_point)
        self.assertIs(face_of_point, dg.root.face)
        self.assertTrue(triangle_face_contains_point(dg.root.face, (13, 19)))


if __name__ == '__main__':
    unittest.main()
