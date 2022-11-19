from triangulation import triangle_face_contains_point
from collections import deque


class Node:
    """ A node in the dual graph.

    Attributes:
    children -- the children nodes (Because the Nodes will be used in the Dual Graph of a triangulated DCEl,
                the children are at most 2)
    parent -- parent of node (None if root)
    face -- Each node corresponds to a face in the triangulated DCEL
    """

    def __init__(self, face, parent):
        self.parent = parent
        self.face = face
        self.children = []


class DualGraph:
    """ Dual graph of a triangulated DCEL

    Attributes:
    :param triangulated_dcel : a triangulated DCEL
    :param face : the face of the triangulated DCEL which corresponds to the root node of the dual graph
    :param target_node : The face found for the path finding algorithm
    """

    def __init__(self, triangulated_dcel, face):
        self.triangulated_dcel = triangulated_dcel

        # self.root = self.create_dual_graph(face, None) (Maximum Recursion Error Python)
        self.root = self.create_dual_graph2(face)

        self.target_node = None

    def create_dual_graph(self, face, parent):
        """ Creates the Dual Graph from triangulated_dcel. Returns the root of the Dual Graph which stores :keyword face

        Keyword arguments:
        :param face : the starting face in the DCEL which corresponds to the returned node's face.
        :param parent : parent of this node. In other words, parent is the node who found the face that corresponds to
                        this node. (None if it's the initial node)
        :returns The root of the dual graph storing :keyword face
        """
        current_node = Node(face, parent)
        if parent is None:  # if it's the root node
            current_node.children = [self.create_dual_graph(f, current_node) for f in self.find_adjacent_faces(face)]
        # If not the root node, we need to be careful to not create circles.
        # parent's face (which is adjacent to this node's face) has already been assigned a node (namely, the parent)
        else:
            current_node.children = [self.create_dual_graph(f, current_node) for f in self.find_adjacent_faces(face)
                                     if f is not parent.face]
        return current_node

    # Iterative counterpart of create_dual_graph. (Maximum Depth Recursion Error Python).
    # https://stackoverflow.com/questions/6809402/python-maximum-recursion-depth-exceeded-while-calling-a-python-object
    def create_dual_graph2(self, face):
        """ Creates the Dual Graph from triangulated_dcel. Returns the root of the Dual Graph which stores :keyword face

        Keyword arguments:
        :param face : the starting face in the DCEL which corresponds to the returned node's face.
        :param parent : parent of this node. In other words, parent is the node who found the face that corresponds to
                        this node. (None if it's the initial node)
        """
        queue = deque()

        # Create root
        root = Node(face, None)
        for f in self.find_adjacent_faces(face):
            new_node = Node(f, root)
            root.children.append(new_node)
            queue.append(new_node)

        while queue:
            current_node = queue.pop()
            for f in self.find_adjacent_faces(current_node.face):
                if f is not current_node.parent.face:
                    new_node = Node(f, current_node)
                    current_node.children.append(new_node)
                    queue.append(new_node)
        return root

    def path_to_point(self, p):
        """ Find path from root node to a face that the point lies in

        Keyword arguments:
        :param p : the query point (tuple with x,y coordinates)
        :returns A list ordered by the sequence of adjacent faces starting from root's face
                 and ending to the face that contains the point p (List of Faces)
        """
        path = []
        # self.find_node_containing_point(self.root, p) . (Maximum Recursion Error Python)
        self.find_node_containing_point2(p)
        tmp_node = self.target_node
        while tmp_node is not None:
            path.insert(0, tmp_node.face)
            tmp_node = tmp_node.parent
        self.target_node = None  # reset
        return path

    def find_node_containing_point(self, node, p):
        """ Find the node which stores the face that contains the point. When found we store it at self.target_node

        Keyword arguments:
        :param node : The node's subtree that the search for the point continues from
        :param p : the query point (tuple with x,y coordinates)
        """
        if self.target_node is not None:
            return
        if triangle_face_contains_point(node.face, p):
            self.target_node = node
            return
        for child in node.children:
            if self.target_node is not None:
                return
            self.find_node_containing_point(child, p)

    # Iterative counterpart of find_node_containing_point. (Maximum Depth Recursion Python)
    # https://stackoverflow.com/questions/6809402/python-maximum-recursion-depth-exceeded-while-calling-a-python-object
    def find_node_containing_point2(self, p):
        """ Find the node which stores the face that contains the point. When found we store it at self.target_node

        Keyword arguments:
        :param p : the query point (tuple with x,y coordinates)
        """
        queue = deque()
        queue.append(self.root)

        while queue:
            tmp_node = queue.pop()
            if triangle_face_contains_point(tmp_node.face, p):
                self.target_node = tmp_node
                return
            for child in tmp_node.children:
                queue.append(child)

    @staticmethod
    def find_adjacent_faces(face):
        """ Given a face of the DCEL return the faces adjacent to this face (excluding unbounded face)

        Keyword arguments:
        :param face : The face for which we will find its adjacent faces (faces that share a diagonal basically)
        :returns The adjacent faces excluding the unbounded face (which we know will be at most 2)
        """
        adjacent_faces = set()

        tmp_hedge = face.outer_component
        while True:
            if tmp_hedge.twin.incident_face.outer_component is not None:  # if adjacent face is not unbounded face
                adjacent_faces.add(tmp_hedge.twin.incident_face)
            tmp_hedge = tmp_hedge.next
            if tmp_hedge is face.outer_component:
                break
        return adjacent_faces


