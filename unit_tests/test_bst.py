import unittest
from src.bst import *
from src.dcel import Hedge, Vertex


class MyTestCase(unittest.TestCase):
    """ This whole suite of tests was created with custom arbitrary segments (following the names of h1,h2,...) ,
    so if your intention is to understand the tests then you must first create the geometry of the segments.
    (we suggest https://www.geogebra.org/geometry?lang=en ) """

    def setUp(self):
        self.h1 = Hedge(Vertex((22.33, 21.05)))
        self.h1.twin = Hedge(Vertex((21.16, 15.65)))

        self.h2 = Hedge(Vertex((21.56, 25.07)))
        self.h2.twin = Hedge(Vertex((38.21, 1.50)))

        self.h3 = Hedge(Vertex((29.21, 19.56)))
        self.h3.twin = Hedge(Vertex((28.73, 16.02)))

        self.h4 = Hedge(Vertex((33.38, 22.27)))
        self.h4.twin = Hedge(Vertex((32.67, 10.19)))

        self.h5 = Hedge(Vertex((34.95, 23.33)))
        self.h5.twin = Hedge(Vertex((33.41, 12.27)))

        self.h6 = Hedge(Vertex((38.27297, 21.56243)))
        self.h6.twin = Hedge(Vertex((37.07312, 4.82169)))

        self.h7 = Hedge(Vertex((22.17378, 23.18687)))
        self.h7.twin = Hedge(Vertex((19.12567, 12.12181)))

        self.h8 = Hedge(Vertex((23.50994, 20.76509)))
        self.h8.twin = Hedge(Vertex((21.5057, 10.91092)))

        self.h9 = Hedge(Vertex((30.50663, 19.43235)))
        self.h9.twin = Hedge(Vertex((32, 16)))

        self.h10 = Hedge(Vertex((35.53536, 21.3079)))
        self.h10.twin = Hedge(Vertex((34.24096, 8.82317)))

        self.h11 = Hedge(Vertex((37.20556, 21.26614)))
        self.h11.twin = Hedge(Vertex((36.28695, 9.03194)))

        self.h12 = Hedge(Vertex((39.08454, 19.92999)))
        self.h12.twin = Hedge(Vertex((38.33295, 8.19685)))

        self.root = None

    def test_delete(self):
        """ Testing deletion, and also checking that after deletion the appropriate half-edge directly to the
        left of specific points in the plane is returned. For example: Notice lines 64-66 where the half-edge directly
        to the left of Vertex((31.27, 18.99)) is the half-edge h3. But after the deletion of h3 the half-edge directly
        to the left of this vertex is h2. This way, we also check that the integrity of the BST is maintained after
        each deletion has occurred.
        """

        # We add h1-h6 because it was easier to keep track of everything geometrically and on paper for the BST
        # (rather than have 12 half-edges and many points in between)
        self.root = insert(self.root, self.h2, self.h2.origin)
        self.root = insert(self.root, self.h5, self.h5.origin)
        self.root = insert(self.root, self.h4, self.h4.origin)
        self.root = insert(self.root, self.h6, self.h6.origin)
        self.root = insert(self.root, self.h1, self.h1.origin)
        self.root = insert(self.root, self.h3, self.h3.origin)

        self.assertIs(find_hedge_directly_to_the_left(self.root, Vertex((31.27, 18.99))), self.h3)
        self.root = delete(self.root, self.h3, self.h3.twin.origin)
        self.assertIs(find_hedge_directly_to_the_left(self.root, Vertex((31.27, 18.99))), self.h2)

        self.root = delete(self.root, self.h1, self.h1.twin.origin)

        self.assertIs(find_hedge_directly_to_the_left(self.root, Vertex((35.95, 18.81))), self.h5)
        self.root = delete(self.root, self.h5, self.h5.twin.origin)
        self.assertIs(find_hedge_directly_to_the_left(self.root, Vertex((35.95, 18.81))), self.h4)

        self.assertIs(find_hedge_directly_to_the_left(self.root, Vertex((35.95, 18.81))), self.h4)
        self.root = delete(self.root, self.h4, self.h4.twin.origin)
        self.assertIs(find_hedge_directly_to_the_left(self.root, Vertex((35.95, 18.81))), self.h2)

        self.assertIs(find_hedge_directly_to_the_left(self.root, Vertex((40.44412, 18.19142))), self.h6)
        self.root = delete(self.root, self.h6, self.h6.twin.origin)
        self.assertIs(find_hedge_directly_to_the_left(self.root, Vertex((40.44412, 18.19142))), self.h2)

        self.root = delete(self.root, self.h2, self.h2.twin.origin)

        self.assertIsNone(self.root)

    def test_find_hedge_directly_to_the_left(self):
        """ Add h1-h12 half-edges and check that the correct half-edge is returned when we query
        vertices in between them and also vertices that lie on them (Obviously we know the geometry beforehand) """

        self.root = insert(self.root, self.h2, self.h2.origin)
        self.root = insert(self.root, self.h5, self.h5.origin)
        self.root = insert(self.root, self.h4, self.h4.origin)
        self.root = insert(self.root, self.h6, self.h6.origin)
        self.root = insert(self.root, self.h1, self.h1.origin)
        self.root = insert(self.root, self.h3, self.h3.origin)
        self.root = insert(self.root, self.h7, self.h7.origin)
        self.root = insert(self.root, self.h9, self.h9.origin)
        self.root = insert(self.root, self.h8, self.h8.origin)
        self.root = insert(self.root, self.h11, self.h11.origin)
        self.root = insert(self.root, self.h10, self.h10.origin)
        self.root = insert(self.root, self.h12, self.h12.origin)

        # Test in between vertices
        self.assertIs(find_hedge_directly_to_the_left(self.root, Vertex((40.44, 18.19))), self.h12)
        self.assertIs(find_hedge_directly_to_the_left(self.root, Vertex((35.95, 18.81))), self.h10)
        self.assertIs(find_hedge_directly_to_the_left(self.root, Vertex((33.70, 19.56))), self.h4)
        self.assertIs(find_hedge_directly_to_the_left(self.root, Vertex((31.27, 18.99))), self.h9)
        self.assertIs(find_hedge_directly_to_the_left(self.root, Vertex((27.58, 18.619))), self.h2)
        self.assertIs(find_hedge_directly_to_the_left(self.root, Vertex((24.10, 18.39))), self.h8)
        self.assertIs(find_hedge_directly_to_the_left(self.root, Vertex((22.38639, 19.17972))), self.h1)

        # Test points that lie on the half-edges (conveniently we choose origin, destination vertices)
        self.assertIs(find_hedge_directly_to_the_left(self.root, self.h1.twin.origin), self.h1)
        self.assertIs(find_hedge_directly_to_the_left(self.root, self.h1.origin), self.h1)

        self.assertIs(find_hedge_directly_to_the_left(self.root, self.h2.twin.origin), self.h2)
        self.assertIs(find_hedge_directly_to_the_left(self.root, self.h2.origin), self.h2)

        self.assertIs(find_hedge_directly_to_the_left(self.root, self.h3.twin.origin), self.h3)
        self.assertIs(find_hedge_directly_to_the_left(self.root, self.h3.origin), self.h3)

        self.assertIs(find_hedge_directly_to_the_left(self.root, self.h4.twin.origin), self.h4)
        self.assertIs(find_hedge_directly_to_the_left(self.root, self.h4.origin), self.h4)

        self.assertIs(find_hedge_directly_to_the_left(self.root, self.h5.twin.origin), self.h5)
        self.assertIs(find_hedge_directly_to_the_left(self.root, self.h5.origin), self.h5)

        self.assertIs(find_hedge_directly_to_the_left(self.root, self.h6.twin.origin), self.h6)
        self.assertIs(find_hedge_directly_to_the_left(self.root, self.h6.origin), self.h6)

        self.assertIs(find_hedge_directly_to_the_left(self.root, self.h7.twin.origin), self.h7)
        self.assertIs(find_hedge_directly_to_the_left(self.root, self.h7.origin), self.h7)

        self.assertIs(find_hedge_directly_to_the_left(self.root, self.h8.twin.origin), self.h8)
        self.assertIs(find_hedge_directly_to_the_left(self.root, self.h8.origin), self.h8)

        self.assertIs(find_hedge_directly_to_the_left(self.root, self.h9.twin.origin), self.h9)
        self.assertIs(find_hedge_directly_to_the_left(self.root, self.h9.origin), self.h9)

        self.assertIs(find_hedge_directly_to_the_left(self.root, self.h10.twin.origin), self.h10)
        self.assertIs(find_hedge_directly_to_the_left(self.root, self.h10.origin), self.h10)

        self.assertIs(find_hedge_directly_to_the_left(self.root, self.h11.twin.origin), self.h11)
        self.assertIs(find_hedge_directly_to_the_left(self.root, self.h11.origin), self.h11)

        self.assertIs(find_hedge_directly_to_the_left(self.root, self.h12.twin.origin), self.h12)
        self.assertIs(find_hedge_directly_to_the_left(self.root, self.h12.origin), self.h12)


if __name__ == '__main__':
    unittest.main()
