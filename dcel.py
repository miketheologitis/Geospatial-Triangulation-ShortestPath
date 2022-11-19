from shapely.geometry import polygon
from itertools import pairwise


class Vertex:
    """ Implementation of a vertex of a 2D dcel """

    def __init__(self, coordinates):
        self.coordinates = coordinates  # Vertex coordinates (x,y)

        # The edge bounding the interior of the polygon that has this Vertex as its origin
        # Note: In the general documentation of DCEL this is defined as 'An arbitrary half-edge TODO: Generalize
        # that has this Vertex as its origin', but because we know we will operate on simple polygons,
        # we redefined it as above. Our definition will be maintained throughout the program.
        self.incident_edge = None

    def is_above(self, vertex):
        """ We define the notions of 'below', 'above' as follows:
        A point p is below another point q if  (p.y < q.y) or (p.y = q.y and p.x > p.x)
        A point p is above another point q if  (p.y > q.y) or (p.y = q.y and p.x < q.x)
        :returns True if the 'instance vertex' is above 'vertex', False otherwise.
        """
        return ((self.coordinates[1] > vertex.coordinates[1]) or
                (self.coordinates[1] == vertex.coordinates[1] and self.coordinates[0] < vertex.coordinates[0]))

    def __str__(self):
        return f'VERTEX - Coordinates: {self.coordinates}'


class Face:
    """ Implementation of a face of a 2D dcel """

    def __init__(self):
        self.outer_component = None  # Some half-edge on its outer boundary. (For the unbounded face its None)
        self.inner_components = []  # Contains for each hole a pointer to some half-edge on the boundary of the hole

    def __str__(self):
        if self.outer_component:
            vertex_list = []
            tmp_hedge = self.outer_component
            while True:
                vertex_list.append(tmp_hedge.origin)
                tmp_hedge = tmp_hedge.next
                if tmp_hedge is self.outer_component:
                    break
            return str([str(v) for v in vertex_list])
        else:
            return "Unbounded Face"


class Hedge:
    """ Implementation of a half-edge of a 2D dcel """

    def __init__(self, origin):
        self.origin = origin  # origin vertex
        self.twin = None  # twin half-edge
        self.incident_face = None  # face that it bounds
        self.next = None  # next edge on the boundary of incident_face
        self.prev = None  # previous edge on the boundary of incident_face

    def __str__(self):
        return f'HEDGE - Origin: {self.origin.coordinates}, Destination: {self.twin.origin.coordinates}'


class Dcel:
    """ Implementation of a doubly-connected edge list.
     We know that the use of Dcel will be to operate on simple polygons. Thus, only the necessary for this project
     functions will be created. TODO: Generalize for polygons with holes """

    def __init__(self):
        self.vertices = []
        self.hedges = []
        self.faces = set()  # Because we want O(1) element removal time complexity

    def build_from_polygon(self, poly):
        """ Build a dcel from a simple polygon (we assume there are no holes!)

        Keyword arguments:
        :param poly : A simple polygon
        """

        # Step 1: Vertex list creation  (Careful: exterior.coords returns a duplicate of the first vertex at the end!)
        for coordinates in polygon.orient(poly).exterior.coords[:-1]:  # counter-clockwise traversal of poly vertices
            self.vertices.append(Vertex(coordinates))

        # Step 2: half-edge list creation. Assignment of twins and vertices
        for v_origin, v_des in pairwise(self.vertices):  # ccw traversal of poly vertices
            h1 = Hedge(v_origin)  # half-edge that bounds the interior face of the polygon
            h2 = Hedge(v_des)  # half-edge that bounds the exterior face of the polygon
            h1.twin = h2
            h2.twin = h1
            v_origin.incident_edge = h1  # Following the definition of incident_edge
            self.hedges.append(h1)
            self.hedges.append(h2)
        # Create half-edge connecting last vertex to the fist vertex (also create the twin)
        h1 = Hedge(self.vertices[-1])
        h2 = Hedge(self.vertices[0])
        h1.twin = h2
        h2.twin = h1
        self.vertices[-1].incident_edge = h1
        self.hedges.append(h1)
        self.hedges.append(h2)

        # Step 3: Identification of next and prev hedges
        # Notice that in the vertex creation above, following the definition of incident_edge, incident edges
        # are always edges that bound the interior face of the polygon. We use this and easily determine
        # the next, prev hedges bellow.
        # ccw traversal of poly half-edges (h1, h2 are always twins, and h1 bounds interior of the polygon)
        for h1, h2 in zip(self.hedges[0::2], self.hedges[1::2]):
            h1_next = h2.origin.incident_edge
            h2_prev = h1_next.twin

            h1.next = h1_next
            h1_next.prev = h1

            h2.prev = h2_prev
            h2_prev.next = h2

        # Step 4: Face assignment (2 faces)
        start_inner_hedge = self.hedges[0]
        start_outer_hedge = self.hedges[1]

        # Unbounded face
        f = Face()
        f.inner_components.append(start_outer_hedge)
        tmp_hedge = start_outer_hedge
        while True:
            tmp_hedge.incident_face = f
            tmp_hedge = tmp_hedge.next
            if tmp_hedge is start_outer_hedge:
                break
        self.faces.add(f)

        # Bounded face
        f = Face()
        f.outer_component = start_inner_hedge
        tmp_hedge = start_inner_hedge
        while True:
            tmp_hedge.incident_face = f
            tmp_hedge = tmp_hedge.next
            if tmp_hedge is start_inner_hedge:
                break
        self.faces.add(f)

    def insert_diagonal(self, v1, v2, f):
        """ Insert diagonal v1v2 in the dcel.

        Keyword arguments:
        :param v1 -- Vertex
        :param v2 -- Vertex
        :param f -- face that the diagonal v1v2 splits
        :return: The inserted half-edge from v1 to v2
        """

        h1 = self.find_hedge_bounding_face_from_origin(v1, f)  # half-edge with origin v1 that bounds face f
        h2 = self.find_hedge_bounding_face_from_origin(v2, f)  # half-edge with origin v2 that bounds face f

        e1 = Hedge(v1)  # half-edge from v1 to v2
        e2 = Hedge(v2)  # half-edge from v2 to v1
        e1.twin = e2
        e2.twin = e1
        self.hedges.append(e1)
        self.hedges.append(e2)

        # For the following assignments a quick drawing with pen and paper would help to visualize.
        # TODO: Generalize for complex polygons

        # Step 1: Connect the next/next attributes of the new e1, e2 half-edges to dcel
        e1.next = h2
        e1.prev = h1.prev
        e2.next = h1
        e2.prev = h2.prev

        # Step 2: Connect the Dcel to the new edges
        h1.prev.next = e1
        h1.prev = e2
        h2.prev.next = e2
        h2.prev = e1

        # Step 3: Remove the old face (which was split in two) and create the two new faces and link them.
        f1 = Face()  # face that is bounded by the newly created half-edge e1
        f2 = Face()  # face that is bounded by the newly created half-edge e2
        self.faces.add(f1)
        self.faces.add(f2)
        self.faces.remove(f)  # O(1) because faces is a set

        f1.outer_component = e1
        f2.outer_component = e2

        # Loop around face f1 and assign every interior edge its new face
        tmp_hedge = e1
        while True:
            tmp_hedge.incident_face = f1
            tmp_hedge = tmp_hedge.next
            if tmp_hedge is e1:
                break

        # Loop around face f2 and assign every interior edge its new face
        tmp_hedge = e2
        while True:
            tmp_hedge.incident_face = f2
            tmp_hedge = tmp_hedge.next
            if tmp_hedge is e2:
                break

        return e1


    @staticmethod
    def find_all_vertices_bounding_face(f):
        """ Given a face f return all vertices around the face in a list """
        vertices = list()
        tmp_hedge = f.outer_component
        while True:
            vertices.append(tmp_hedge.origin)
            tmp_hedge = tmp_hedge.next
            if tmp_hedge is f.outer_component:
                break
        return vertices

    @staticmethod
    def find_hedge_bounding_face_from_origin(v, f):
        """ Given a vertex v and a face f return the half-edge that has as origin v and bounds f """
        hedge = v.incident_edge
        while hedge.incident_face is not f:
            hedge = hedge.prev.twin
        return hedge

    @staticmethod
    def find_hedge_connecting_origin_dest(orig, dest):
        """ Given a vertex orig and a vertex dest find the half-edge from orig to dest """
        hedge = orig.incident_edge
        while hedge.twin.origin is not dest:
            hedge = hedge.prev.twin
        return hedge

    @staticmethod
    def find_common_face_for_diagonal(v1, v2):
        """ Given two vertices v1, v2 where we know for a fact that a diagonal v1v2 is valid, find distinct face
        that will be cute in half by the diagonal """

        # Step 1: Find all faces that have v1 in their perimeter
        v1_faces = set()

        # loop around all half-edges with origin v1 and store incident_faces
        hedge = v1.incident_edge
        while True:
            v1_faces.add(hedge.incident_face)
            hedge = hedge.prev.twin
            if hedge is v1.incident_edge:
                break

        # loop around all half-edges with origin v2 and if the incident_face is in v1_faces (and is not the unbounded
        # face) then return it. Remember: We know for a fact that this face exists and is distinct
        # (because the diagonal v1v2 is valid)
        hedge = v2.incident_edge
        while True:
            if hedge.incident_face in v1_faces and hedge.incident_face.outer_component is not None:
                return hedge.incident_face
            hedge = hedge.prev.twin
