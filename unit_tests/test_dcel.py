import unittest
from src.dcel import Dcel, Vertex
from shapely.geometry import Polygon
import matplotlib.pyplot as plt


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.polygon_dcel = Dcel()
        self.poly = Polygon([
            (114.0, -8.590444), (113.998361, -8.592111), (110.7075, -8.202111), (108.862528, -7.609583),
            (107.843306, -7.739583), (106.401667, -7.384639), (106.505, -6.965472), (105.207111, -6.751694),
            (105.797944, -6.489167), (106.038333, -5.874611), (108.3025, -6.240389), (108.932472, -6.841306),
            (110.406667, -6.952083), (111.029167, -6.416278), (112.547472, -6.842917), (113.155833, -7.74625),
            (114.438333, -7.78875), (114.592917, -8.752528)
        ])
        # Polygon from a dataset
        self.polygon_dcel.build_from_polygon(self.poly)

    def test_hedges_no_none_attribute(self):
        """ Test if all edges have no None attributes """
        for hedge in self.polygon_dcel.hedges:
            self.assertIsNotNone(hedge.origin)
            self.assertIsNotNone(hedge.twin)
            self.assertIsNotNone(hedge.next)
            self.assertIsNotNone(hedge.incident_face)
            self.assertIsNotNone(hedge.prev)

    def test_hedges_twin(self):
        """ Test twin edges """
        for hedge in self.polygon_dcel.hedges:
            self.assertIsNot(hedge, hedge.twin)
            self.assertIs(hedge, hedge.twin.twin)

    def test_hedges_origin(self):
        """ Test origin of hedges """
        for hedge in self.polygon_dcel.hedges:
            self.assertIsNot(hedge.origin, hedge.twin.origin)
            self.assertIs(hedge.origin, hedge.prev.twin.origin)

    def test_hedges_next_prev_of_polygon(self):
        """ For all half-edges test next/prev half-edges (also using twins) for a simple polygon dcel. With this test
        we confirm that next, prev edges are correctly linked in the creation of a simple polygon dcel.
        """
        for hedge in self.polygon_dcel.hedges:
            self.assertIsNot(hedge, hedge.next)
            self.assertIsNot(hedge, hedge.prev)
            self.assertIs(hedge, hedge.next.prev)
            self.assertIs(hedge, hedge.prev.next)
            self.assertIs(hedge, hedge.next.twin.next.twin)
            self.assertIs(hedge, hedge.twin.prev.twin.prev)
            self.assertIs(hedge, hedge.prev.twin.prev.twin)
            self.assertIs(hedge, hedge.twin.next.twin.next)

    def test_hedges_next_prev_with_diagonals(self):
        """ For all half-edges test next/prev half-edges for a dcel of a simple polygons where diagonals have been
        inserted. Note that this test is simpler than test_edges_next_prev_of_polygon because of the existence
        of diagonals.
        """
        for hedge in self.polygon_dcel.hedges:
            self.assertIsNot(hedge, hedge.next)
            self.assertIsNot(hedge, hedge.prev)
            self.assertIs(hedge, hedge.next.prev)
            self.assertIs(hedge, hedge.prev.next)

    def test_faces_unbounded_and_bounded(self):
        """ Test that the unbounded face exists (check if there exists a face where outer_component is None)
        and all other faces have outer_component != None
        """
        unbounded_face = None
        for f in self.polygon_dcel.faces:  # find unbounded face (also check that only 1 unbounded face exists)
            if f.outer_component is None:
                self.assertIsNone(unbounded_face)  # check that only 1 unbounded face exists
                unbounded_face = f
                self.assertTrue(unbounded_face.inner_components)  # check that inner_components is not empty
        for f in self.polygon_dcel.faces:
            if f is unbounded_face:
                continue
            self.assertIsNotNone(f.outer_component)

    def test_faces_and_hedge_incident_face_link(self):
        """ Test that for each half-edge the incident_face is correctly linked (and the reverse)
        TODO: We assume that inner faces do not have holes (and thus we don't check inner_components in inner faces!)
        """
        for f in self.polygon_dcel.faces:
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

    @unittest.skip("Skip because it is a visual test with a plot and terminal output!")
    def test_geometry_of_dcel(self):
        """ Visual testing (with a plot and terminal output) for each vertex and its assigned type """
        i = 0
        for vertex in self.polygon_dcel.vertices:
            print("Vertex {}, Coordinates {}".format(i, vertex.coordinates))
            i += 1
        i = 0
        for hedge in self.polygon_dcel.hedges:
            print("Hedge Pair {}, Origin {}, Twin Origin {}".format(
                i, hedge.origin.coordinates, hedge.twin.origin.coordinates
                )
            )
            i += 1
        x, y = self.poly.exterior.xy
        plt.plot(x, y)
        plt.show()

    def test_vertex_is_above(self):
        """ Test Vertex class method is_above """
        v1 = Vertex((1, 1))
        v2 = Vertex((0, 0))
        v3 = Vertex((0, 1))
        self.assertTrue(v1.is_above(v2))
        self.assertFalse(v1.is_above(v3))
        self.assertFalse(v2.is_above(v3))
        self.assertTrue(v3.is_above(v2))

    def test_insert_diagonal(self):
        """ Test insert_diagonal function from known to exist valid diagonals. Also check everything
        is still working in dcel by running all the above tests again after the diagonal insertions.
        """
        def find_common_face(v1, v2):  # O(n^2)
            h1 = v1.incident_edge
            h2 = v2.incident_edge
            while True:
                h2_tmp = h2
                while True:
                    if h2_tmp.incident_face is h1.incident_face:
                        return h1.incident_face
                    h2_tmp = h2_tmp.prev.twin
                    if h2_tmp is h2:
                        break
                h1 = h1.prev.twin

        # Insert valid diagonals with tricky order (including diagonal insertion between two previous diagonal
        # insertions)
        self.polygon_dcel.insert_diagonal(
            self.polygon_dcel.vertices[15], self.polygon_dcel.vertices[8],
            find_common_face(self.polygon_dcel.vertices[15], self.polygon_dcel.vertices[8])
        )
        self.polygon_dcel.insert_diagonal(
            self.polygon_dcel.vertices[15], self.polygon_dcel.vertices[9],
            find_common_face(self.polygon_dcel.vertices[15], self.polygon_dcel.vertices[9])
        )
        self.polygon_dcel.insert_diagonal(
            self.polygon_dcel.vertices[15], self.polygon_dcel.vertices[4],
            find_common_face(self.polygon_dcel.vertices[15], self.polygon_dcel.vertices[4])
        )
        self.polygon_dcel.insert_diagonal(
            self.polygon_dcel.vertices[15], self.polygon_dcel.vertices[6],
            find_common_face(self.polygon_dcel.vertices[15], self.polygon_dcel.vertices[6])
        )
        self.polygon_dcel.insert_diagonal(
            self.polygon_dcel.vertices[15], self.polygon_dcel.vertices[7],
            find_common_face(self.polygon_dcel.vertices[15], self.polygon_dcel.vertices[7])
        )

        # Run above tests again
        self.test_hedges_origin()
        self.test_hedges_no_none_attribute()
        self.test_hedges_twin()
        self.test_hedges_next_prev_with_diagonals()  # custom test for this purpose
        self.test_faces_unbounded_and_bounded()
        self.test_faces_and_hedge_incident_face_link()


if __name__ == '__main__':
    unittest.main()
