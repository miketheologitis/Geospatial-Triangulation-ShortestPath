from .dcel import Dcel
from .bst import insert, delete, find_hedge_directly_to_the_left
from shapely.geometry import Polygon
from numpy import array, clip, arccos, dot, cross, rad2deg
from numpy.linalg import norm

""" This module is responsible for triangulating a polygon. It is a direct implementation of 
Chapter 3: Computational Geometry, Third Edition, Marc de Berg. All the following functions are 
explained in great detail in Chapter 3 of this book. Thus, the comments/clarifications of the following code
will mostly focus on deviations of the explained solution in Chapter 3.

Important problem definitions:
Let v_1, v_2, v_3, ..., v_n be a counterclockwise enumeration of the vertices of a Polygon. Let e_1, e_2, ..., e_n
be the set of edges of the Polygon, where e_i = v_i v_i+1 and e_n = v_n v_1 . Because we are talking about ccw 
enumeration e_i is v_i.incident_edge (as defined in dcel.py). Moreover, e_(i-1) = v_i.incident_edge.twin.next.twin.

(Note: e_(i-1) = v_i.incident_edge.prev BUT when diagonals are added this isn't correct anymore. So we follow the 
definition above)
"""


def make_monotone(poly):
    """ Returns A partitioning of a polygon into monotone sub-polygons, stored in a DCEL.
    (Page 53, Computational Geometry, Mark de Berg)

    Keyword arguments:
    :param poly: A shapely simple Polygon
    """
    # We need to find the edge to the left of each vertex, therefore we store the ccw half-edges of the Polygon
    # intersecting the sweep line in a BST. The inorder traversal of the BST corresponds to a left to right
    # order of the half-edges intersecting the sweep line.
    # (This BST along with the 'helper' dictionary form the status of the sweep line algorithm)
    root = None

    # Dictionary distinguishing for each Dcel polygon vertex its type. To be used for triangulating a polygon.
    # key: Hedge , value: String distinguishing the type
    vertex_type = dict()

    # The lowest vertex above the sweep line such that the horizontal segment connecting the vertex to a half-edge
    # lies inside the Polygon.
    # Key: Hedge , value: Vertex
    helper = dict()

    polygon_dcel = Dcel()  # init DCEL

    polygon_dcel.build_from_polygon(poly)  # build DCEL

    # assign the type attribute to all dcel vertices (in vertex_type dict)
    assign_type_to_vertices(polygon_dcel, vertex_type)

    # Sort the vertices on y-coordinate before the sweep. If two vertices have the same y-coordinate then
    # the leftmost one has higher priority. Thus, we first sort on ascending order for x-coordinate (secondary key),
    # and then sort on descending order for y-coordinate (primary key)
    queue = sorted(
        sorted(polygon_dcel.vertices, key=lambda vertex: vertex.coordinates[0]),
        key=lambda vertex: vertex.coordinates[1],
        reverse=True
    )

    while queue:
        v_i = queue.pop(0)
        match vertex_type[v_i]:
            case "start vertex":
                root = handle_start_vertex(root, helper, v_i)
            case "split vertex":
                root = handle_split_vertex(polygon_dcel, root, helper, v_i)
            case "end vertex":
                root = handle_end_vertex(polygon_dcel, root, helper, vertex_type, v_i)
            case "merge vertex":
                root = handle_merge_vertex(polygon_dcel, root, helper, vertex_type, v_i)
            case "regular vertex":
                root = handle_regular_vertex(polygon_dcel, root, helper, vertex_type, v_i)
    return polygon_dcel


def handle_start_vertex(root, helper, v_i):
    """ (Page 53, Computational Geometry, third edition, Mark de Berg)

    Keyword arguments:
    :param root : root of BST
    :param helper: Dictionary storing for each half-edge the helper Vertex. Key: Hedge , Value: Vertex
    :param v_i : Vertex that the sweep line intersects at the moment
    """
    e_i = v_i.incident_edge

    root = insert(root, e_i, v_i)  # insert half-edge e_i to BST when sweep line is at vertex v_i
    helper[e_i] = v_i  # Set helper(e_i) to v_i
    return root


def handle_end_vertex(d, root, helper, vertex_type, v_i):
    """ (Page 53, Computational Geometry, third edition, Mark de Berg)

    Keyword arguments:
    :param d : dcel
    :param root : root of BST
    :param helper: Dictionary storing for each half-edge the helper Vertex. Key: Hedge , Value: Vertex
    :param vertex_type : dictionary with key: Vertex, value: The type of vertex
    :param v_i : Vertex that the sweep line intersects at the moment
    """
    e_i_minus_1 = v_i.incident_edge.twin.next.twin  # e_(i-1)

    if vertex_type[helper[e_i_minus_1]] == "merge vertex":  # if helper(e_(i-1)) is a merge vertex
        # Then insert the diagonal connecting v_i to helper(e_(i-1)) in the DCEL (which splits e_(i-1).incident_face)
        d.insert_diagonal(v_i, helper[e_i_minus_1], e_i_minus_1.incident_face)
    root = delete(root, e_i_minus_1, v_i)  # Remove e_(i-1) from BST when sweep line is at vertex v_i

    return root


def handle_split_vertex(d, root, helper, v_i):
    """ (Page 54, Computational Geometry, third edition, Mark de Berg)

    Keyword arguments:
    :param d : dcel
    :param root : root of BST
    :param helper: Dictionary storing for each half-edge the helper Vertex. Key: Hedge , Value: Vertex
    :param v_i : Vertex that the sweep line intersects at the moment
    """
    e_i = v_i.incident_edge

    # Search BST to find the edge e_j directly left of v_i
    e_j = find_hedge_directly_to_the_left(root, v_i)

    # Insert diagonal connecting v_i to helper(e_j) in DCEL (which splits e_j.incident_face)
    d.insert_diagonal(v_i, helper[e_j], e_j.incident_face)

    helper[e_j] = v_i  # Set helper(e_j) to v_i
    root = insert(root, e_i, v_i)  # insert half-edge e_i to BST when sweep line is at vertex v_i
    helper[e_i] = v_i  # Set helper(e_i) to v_i

    return root


def handle_merge_vertex(d, root, helper, vertex_type, v_i):
    """ (Page 54, Computational Geometry, third edition, Mark de Berg)

    Keyword arguments:
    :param d : dcel
    :param root : root of BST
    :param helper: Dictionary storing for each half-edge the helper Vertex. Key: Hedge , Value: Vertex
    :param vertex_type : dictionary with key: Vertex, value: The type of vertex
    :param v_i : Vertex that the sweep line intersects at the moment
    """
    e_i_minus_1 = v_i.incident_edge.twin.next.twin  # e_(i-1)

    if vertex_type[helper[e_i_minus_1]] == "merge vertex":  # if helper(e_(i-1)) is a merge vertex
        # Then insert the diagonal connecting v_i to helper(e_(i-1)) in the DCEL (which splits e_(i-1).incident_face)
        d.insert_diagonal(v_i, helper[e_i_minus_1], e_i_minus_1.incident_face)

    root = delete(root, e_i_minus_1, v_i)  # Delete e_(i-1) from BST when sweep line is at vertex v_i

    # Search in BST to find the edge e_j directly left of v_i
    e_j = find_hedge_directly_to_the_left(root, v_i)

    if vertex_type[helper[e_j]] == "merge vertex":  # if helper(e_j) is a merge vertex
        # Then insert the diagonal connecting v_i to helper(e_j) in the DCEL (which splits e_j.incident_face)
        d.insert_diagonal(v_i, helper[e_j], e_j.incident_face)

    helper[e_j] = v_i  # Set helper(e_j) to v_i

    return root


def handle_regular_vertex(d, root, helper, vertex_type, v_i):
    """ (Page 54, Computational Geometry, third edition, Mark de Berg)

    Keyword arguments:
    :param d: dcel
    :param root: root of BST
    :param helper: Dictionary storing for each half-edge the helper Vertex. Key: Hedge , Value: Vertex
    :param vertex_type: Dictionary storing for each Vertex its type. Key: Vertex, Value: The type of vertex (String)
    :param v_i: Vertex that the sweep line intersects at the moment
    """
    e_i = v_i.incident_edge  # e_i
    e_i_minus_1 = e_i.twin.next.twin  # e_(i-1)

    v_i_minus_1 = e_i_minus_1.origin  # v_(i-1)
    v_i_plus_1 = v_i.incident_edge.twin.origin  # v_(i+1)

    # TODO: think this through more
    # if the interior of the polygon lies to the right of v_i. We are dealing with a regular vertex, thus,
    # the interior of the polygon lies to the right of v_i only when v_(i-1) is above v_(i+1)
    if v_i_minus_1.is_above(v_i_plus_1):
        if vertex_type[helper[e_i_minus_1]] == "merge vertex":  # if helper(e_(i-1)) is a merge vertex
            # Then insert the diagonal connecting v_i to helper(e_(i-1)) in DCEL (which splits e_(i-1).incident_face)
            d.insert_diagonal(v_i, helper[e_i_minus_1], e_i_minus_1.incident_face)
        root = delete(root, e_i_minus_1, v_i)  # Remove e_(i-1) from BST when sweep line is at vertex v_i
        root = insert(root, e_i, v_i)  # insert half-edge e_i to BST when sweep line is at vertex v_i
        helper[e_i] = v_i
    else:
        # Search in BST to find the edge e_j directly left of v_i
        e_j = find_hedge_directly_to_the_left(root, v_i)
        if vertex_type[helper[e_j]] == "merge vertex":  # if helper(e_j) is a merge vertex
            # Then insert the diagonal connecting v_i to helper(e_j) in the DCEL (which splits e_j.incident_face)
            d.insert_diagonal(v_i, helper[e_j], e_j.incident_face)
        helper[e_j] = v_i

    return root


def assign_type_to_vertices(d, vertex_type):
    """ Assign the type attribute to all dcel vertices.

    Keyword arguments:
    :param d : dcel
    :param vertex_type : dictionary with key: Vertex, Value: The type of vertex  (To be assigned)
    """
    start_inner_hedge = d.hedges[0]  # we know for a fact hedges[0] is a half-edge bounding the interior face

    tmp_hedge = start_inner_hedge
    while True:
        # we are always assigning the type of v_b (the middle vertex)
        assign_type_to_vertex(vertex_type, tmp_hedge.prev.origin, tmp_hedge.origin, tmp_hedge.next.origin)
        tmp_hedge = tmp_hedge.next
        if tmp_hedge is start_inner_hedge:
            break


def assign_type_to_vertex(vertex_type, v_a, v_b, v_c):

    """ Assign the type attribute to a dcel vertex. We assign type to v_b only.

    Keyword arguments:
    :param vertex_type: dictionary with key: Vertex, value: The type of vertex (To be assigned)
    :param v_a: Vertex before v_b
    :param v_b: Vertex after v_a and before v_c, that is to be assigned a type
    :param v_c: Vertex after v_b

    We distinguish 5 types of polygon vertices (1-4 'turn' vertices):
    1. "start vertex" : If its two neighbors lie below it and the interior angle is less than 180
    2. "split vertex" : If its two neighbors lie below it and the interior angle is greater than 180
    3. "end vertex" : If its two neighbors lie above it and the interior angle is less than 180
    4. "merge vertex" : If its two neighbors lie above it and the interior angle is greater than 180
    5. "regular vertex" : Not 'turn' vertices. (not any of the 1-4)
    """
    if (angle_between_points_ccw(v_a.coordinates, v_b.coordinates, v_c.coordinates) < 180
            and v_b.is_above(v_a) and v_b.is_above(v_c)):
        vertex_type[v_b] = "start vertex"
    elif (angle_between_points_ccw(v_a.coordinates, v_b.coordinates, v_c.coordinates) > 180
          and v_b.is_above(v_a) and v_b.is_above(v_c)):
        vertex_type[v_b] = "split vertex"
    elif (angle_between_points_ccw(v_a.coordinates, v_b.coordinates, v_c.coordinates) < 180
          and (not v_b.is_above(v_a)) and (not v_b.is_above(v_c))):
        vertex_type[v_b] = "end vertex"
    elif (angle_between_points_ccw(v_a.coordinates, v_b.coordinates, v_c.coordinates) > 180
          and (not v_b.is_above(v_a)) and (not v_b.is_above(v_c))):
        vertex_type[v_b] = "merge vertex"
    else:
        vertex_type[v_b] = "regular vertex"


def triangulate_monotone_polygon(d, f):
    """ Triangulates y-monotone polygon defined by a face in the dcel and stores it in the dcel.
    Page 57, Computational Geometry, third edition, Mark de Berg
    :param d: dcel storing the y-monotone polygon
    :param f: face of the y-monotone polygon (to be triangulated) stored in the dcel
    """

    # Sort the vertices on y-coordinate before the sweep. If two vertices have the same y-coordinate then
    # the leftmost one has higher priority. Thus, we first sort on increasing order for x-coordinate (secondary key),
    # and then sort on decreasing order for y-coordinate (primary key)
    vertices = sorted(
        sorted(d.find_all_vertices_bounding_face(f), key=lambda vertex: vertex.coordinates[0]),
        key=lambda vertex: vertex.coordinates[1],
        reverse=True
    )

    # left_chain , right_chain both contain the top/bottom vertices (vertices[0], vertices[-1])
    left_chain, right_chain = left_right_chains(f, vertices[0], vertices[-1])

    stack = [vertices[0], vertices[1]]

    for j, v_j in enumerate(vertices[2:-1], start=2):

        # v_j in left_chain and vertex at the top of stack at right_chain. They lie on different chains
        if v_j in left_chain and stack[-1] in right_chain:
            # based on the geometry of the funnel in this case: bottom of stack is connected to v_j and the face
            # in which a diagonal (might) be inserted is exactly the face that is bounded by the half-edge
            # connecting the bottom of the stack with v_j
            next_face_to_be_split = d.find_hedge_connecting_origin_dest(stack[0], v_j).incident_face

            while stack:  # while stack is not empty
                u = stack.pop(-1)
                if stack:  # If stack not empty
                    # Insert diagonal connecting v_j to u. The diagonal splits the face next_face_to_be_split.
                    # insert_diagonal also returns the new inserted half-edge diagonal v_j to u , hence, based on the
                    # geometry of the funnel in this case, the incident_face of the returned half-edge is the new
                    # interior face of the funnel. (In the next diagonal insertion that is the face that will be split)
                    next_face_to_be_split = d.insert_diagonal(v_j, u, next_face_to_be_split).incident_face
            stack.append(vertices[j-1])  # push v_(j-1) onto the stack
            stack.append(v_j)  # push v_j onto the stack

        # v_j in right_chain and vertex at the top of stack at left_chain. They lie on different chains
        elif v_j in right_chain and stack[-1] in left_chain:
            # based on the geometry of the funnel in this case: bottom of stack is connected to v_j and the face
            # in which a diagonal (might) be inserted is exactly the face that is bounded by the half-edge
            # connecting v_j to the vertex at the bottom of the stack
            next_face_to_be_split = d.find_hedge_connecting_origin_dest(v_j, stack[0]).incident_face

            while stack:  # while stack is not empty
                u = stack.pop(-1)
                if stack:  # If stack not empty
                    # Insert diagonal connecting v_j to u. The diagonal splits the face next_face_to_be_split.
                    # insert_diagonal also returns the new inserted half-edge diagonal v_j to u , hence, based on the
                    # geometry of the funnel in this case, the incident_face of the returned half-edge's twin is the new
                    # interior face of the funnel. (In the next diagonal insertion that is the face that will be split)
                    next_face_to_be_split = d.insert_diagonal(v_j, u, next_face_to_be_split).twin.incident_face
            stack.append(vertices[j - 1])  # push v_(j-1) onto the stack
            stack.append(v_j)  # push v_j onto the stack

        # v_j in right_chain and vertex at the top of stack in right_chain. They lie on the same chain. Also, when
        # this is true, v_j is already connected to the top of stack.
        elif v_j in right_chain and stack[-1] in right_chain:
            u = stack.pop(-1)

            # based on the geometry of the funnel in this case: v_j is connected to the top of stack (u vertex) and
            # the face in which a diagonal (might) be inserted is exactly the face that is bounded by the half-edge
            # connecting v_j to the vertex u
            next_face_to_be_split = d.find_hedge_connecting_origin_dest(v_j, u).incident_face

            # while stack not empty and a diagonal from v_j to top of stack is inside the polygon.
            while stack and ccw(v_j.coordinates, u.coordinates, stack[-1].coordinates):
                u = stack.pop(-1)

                # Insert diagonal connecting v_j to u. The diagonal splits the face next_face_to_be_split.
                # insert_diagonal also returns the new inserted half-edge diagonal v_j to u , hence, based on the
                # geometry of the funnel in this case, the incident_face of the returned half-edge is the new
                # interior face of the funnel. (In the next diagonal insertion that is the face that will be split)
                next_face_to_be_split = d.insert_diagonal(v_j, u, next_face_to_be_split).incident_face
            stack.append(u)  # Push the last vertex that has been popped back onto the stack
            stack.append(v_j)  # push v_j onto the stack

        # v_j in left_chain and vertex at the top of stack in left_chain. They lie on the same chain.
        else:
            u = stack.pop(-1)

            # based on the geometry of the funnel in this case: v_j is connected to the top of stack (u vertex) and
            # the face in which a diagonal (might) be inserted is exactly the face that is bounded by the half-edge
            # connecting u (the vertex that was popped from the top of stack) to v_j
            next_face_to_be_split = d.find_hedge_connecting_origin_dest(u, v_j).incident_face

            # while stack not empty and a diagonal from v_j to top of stack is inside the polygon
            while stack and not ccw(v_j.coordinates, u.coordinates, stack[-1].coordinates):
                u = stack.pop(-1)

                # Insert diagonal connecting v_j to u. The diagonal splits the face next_face_to_be_split.
                # insert_diagonal also returns the new inserted half-edge diagonal v_j to u , hence, based on the
                # geometry of the funnel in this case, the incident_face of the returned half-edge's twin is the new
                # interior face of the funnel. (In the next diagonal insertion that is the face that will be split)
                next_face_to_be_split = d.insert_diagonal(v_j, u, next_face_to_be_split).twin.incident_face
            stack.append(u)  # Push the last vertex that has been popped back onto the stack
            stack.append(v_j)  # push v_j onto the stack

    # Add diagonals from v_n (lowest y-coordinate vertex in vertices) to all stack vertices except the first
    # and the last one. Note that because we cannot be certain of the geometry of the last vertices in the stack
    # we cannot find the face that will be split by the diagonal very quickly (like above). This is why we use the
    # find_common_face_for_diagonal function which basically returns in a brute force way that distinct face given
    # only the two vertices. (Read the function comments for more info). The leftover stack vertices are VERY, VERY rare
    stack.pop(0)
    stack.pop(-1)
    v_n = vertices[-1]
    while stack:
        u = stack.pop(-1)
        d.insert_diagonal(v_n, u, d.find_common_face_for_diagonal(v_n, u))


def triangulate_polygon(poly):
    """ Triangulates a simple polygon

    Keyword arguments:
    :param poly: A simple polygon to be triangulated
    :return: the DCEL storing the triangulated polygon
    """
    dcel_triangulated = make_monotone(poly)
    faces = dcel_triangulated.faces.copy()  # because we are going to add faces
    for f in faces:
        if f.outer_component is not None:  # not unbounded face
            triangulate_monotone_polygon(dcel_triangulated, f)
    return dcel_triangulated


def left_right_chains(f, top_v, bot_v):
    """ Given a face f of a y-monotone polygon and the vertices at the top/bottom of the left/right polygonal chains,
    return the left and right polygonal chains.

    Keyword arguments:
    :param f: the face f of the y-monotone polygon in the DCEL
    :param top_v: the vertex at the top of the left/right polygonal chains
    :param bot_v: the vertex at the bottom of the left/right polygonal chains
    :return: the left and right polygonal chains.
    """

    left_chain = {top_v, bot_v}  # set - left chain of the y-monotone polygon (including top/bot vertices)
    right_chain = {top_v, bot_v}  # set - right chain of the y-monotone polygon (including top/bot vertices)

    # Locate top half-edge (that is, the half-edge bounding the polygon with origin the top vertex)
    tmp_hedge = f.outer_component
    while True:
        if tmp_hedge.origin is top_v:  # Then top half-edge is tmp_hedge
            top_h = tmp_hedge
            break
        tmp_hedge = tmp_hedge.next

    tmp_hedge = top_h  # start from next half-edge from top half-edge
    add_to_left_chain = True  # boolean that tells us whether we add to the left or right chain
    while True:  # Loop around face in ccw, first adding vertices of the left chain and then of the right chain
        if add_to_left_chain:
            left_chain.add(tmp_hedge.origin)
        else:
            right_chain.add(tmp_hedge.origin)
        tmp_hedge = tmp_hedge.next

        if tmp_hedge.origin is bot_v:  # reached bottom vertex, so now we are at the right chain part
            add_to_left_chain = False
        if tmp_hedge is top_h:
            break

    return left_chain, right_chain


def angle_between_points_ccw(a, b, c):
    """ Given points a,b,c return the angle (in degrees) abc in respect to ccw rotation.
    (In other words, slightly abusing correct terminology, we can think that we move from a to b to c and the angle
    abc this function returns is always the one to left of us!)

    Keyword arguments:
    :param a: coordinates of the form (x,y). Point before b.
    :param b: coordinates of the form (x,y). Point after a and before c.
    :param c: coordinates of the form (x,y). Point after a.
    :return: The angle (in degrees) abc in respect to ccw rotation.
    """
    ba = array(a) - array(b)  # vector from b to a
    bc = array(c) - array(b)  # vector from b to c
    if ccw(a, b, c):  # if abc is counter-clockwise then the angle is 0-179.99... and all is good
        # Note: Due to floating-point presicion dot() can return 1.0000000000000002 so we have to be safe
        return rad2deg(arccos(clip(dot(ba, bc) / (norm(ba) * norm(bc)), -1, 1)))
    # abc is not ccw, thus the angle is reflex. Notice we (mod 360) and that is because if points are collinear
    # we want 0 degrees and NOT 360 degrees.
    # Note: Due to floating-point presicion dot() can return 1.0000000000000002 so we have to be safe
    return (360 - rad2deg(arccos(clip(dot(ba, bc) / (norm(ba) * norm(bc)), -1, 1)))) % 360


def ccw(a, b, c):
    return cross(array(b) - array(a), array(c) - array(b)) > 0


def point_in_triangle(a, b, c, p):
    """ Checks whether a point lies in the given triangle

    :param a: First vertex of the triangle (tuple with x and y coordinate)
    :param b: Second vertex of the triangle (tuple with x and y coordinate)
    :param c: Third vertex of the triangle (tuple with x and y coordinate)
    :param p: The point to be checked (tuple with x any y coordinate)
    :return: True if the point lies in the triangle, False otherwise
    """
    a = array(a)
    b = array(b)
    c = array(c)
    p = array(p)

    ab = b - a
    bc = c - b
    ca = a - c

    ap = p - a
    bp = p - b
    cp = p - c

    ab_cross_ap = cross(ab, ap)
    bc_cross_bp = cross(bc, bp)
    ca_cross_cp = cross(ca, cp)

    # TODO: Deal with the case where point lies on the edge for shortest path algo

    if ab_cross_ap == 0:  # points a,b,p collinear. Check if point p lies on segment ab
        if (min(a[0], b[0]) <= p[0] <= max(a[0], b[0])) and (min(a[1], b[1]) <= p[1] <= max(a[1], b[1])):
            return True
        return False

    if bc_cross_bp == 0:  # points b,c,p collinear. Check if point p lies on segment bc
        if (min(c[0], b[0]) <= p[0] <= max(c[0], b[0])) and (min(c[1], b[1]) <= p[1] <= max(c[1], b[1])):
            return True
        return False

    if ca_cross_cp == 0:  # points a,c,p collinear. Check if point p lies on segment bc
        if (min(c[0], a[0]) <= p[0] <= max(c[0], a[0])) and (min(c[1], a[1]) <= p[1] <= max(c[1], a[1])):
            return True
        return False

    if ((ab_cross_ap > 0 and bc_cross_bp > 0 and ca_cross_cp > 0) or
            (ab_cross_ap < 0 and bc_cross_bp < 0 and ca_cross_cp < 0)):
        return True
    return False


def triangle_face_contains_point(face, p):
    triangle_coordinates = []
    tmp_hedge = face.outer_component
    while True:
        triangle_coordinates.append(tmp_hedge.origin.coordinates)
        tmp_hedge = tmp_hedge.next
        if tmp_hedge is face.outer_component:
            break
    return point_in_triangle(triangle_coordinates[0], triangle_coordinates[1], triangle_coordinates[2], p)


def find_triangle_face_containing_point(triangulated_dcel, p):
    """
    For a triangulated dcel find the face that the point lies in

    :param triangulated_dcel : a triangulated dcel
    :param p: point p
    :return: The face
    """
    for f in triangulated_dcel.faces:
        if f.outer_component is None:
            continue
        if triangle_face_contains_point(f, p):
            return f


