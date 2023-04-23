

class Node:
    def __init__(self, hedge):
        self.left = None
        self.right = None
        self.hedge = hedge


def insert(root, hedge, vertex):
    """ Insert into the BST based on the x-coordinate of the intersection point between 'hedge' and the parallel to
    x'x sweep line that passes through 'vertex'. We know for a fact that this intersection point exists and is to the
    left of the vertex. Moreover, there can't be two hedges with the same x-coordinate of the intersection point
    because it would mean these two hedges intersect (and this isn't possible because they belong to a polygon)

    Keyword arguments:
    :param root : root of BST
    :param hedge : half-edge to be inserted to BST
    :param vertex : Location of parallel to x'x sweep line (Sweep line intersects vertex at this point). Will help us
                    guide the search down BST.
    """

    if root is None:
        return Node(hedge)

    # No need to check equality as explained above.
    if x_intersection_coord(hedge, vertex) > x_intersection_coord(root.hedge, vertex):  # hedge belongs to the right
        root.right = insert(root.right, hedge, vertex)
    else:
        root.left = insert(root.left, hedge, vertex)

    return root


def min_value_node(node):
    """ Returns the leftmost half-edge stored in the subtree rooted at :param node"""
    current = node
    while current.left is not None:
        current = current.left
    return current


def delete(root, hedge, vertex):
    """ Delete node that stores 'hedge' from BST

    Keyword arguments:
    :param root : root of BST
    :param hedge : half-edge to be deleted from BST
    :param vertex : Location of parallel to x'x sweep line (Sweep line intersects vertex at this point). Will help us guide
                    the search down BST.
    :returns The (possibly new) root of BST
    """
    if root is None:
        return root

    if x_intersection_coord(hedge, vertex) > x_intersection_coord(root.hedge, vertex):  # 'hedge' lies to the right
        root.right = delete(root.right, hedge, vertex)
    elif x_intersection_coord(hedge, vertex) < x_intersection_coord(root.hedge, vertex):  # 'hedge' lies to the left
        root.left = delete(root.left, hedge, vertex)
    else:  # This is the node to be deleted (because we are dealing with polygon half-edges)
        # Node with only one child or no child
        if root.left is None:
            tmp = root.right
            root = None
            return tmp
        elif root.right is None:
            tmp = root.left
            root = None
            return tmp

        # Node with two children: Get the inorder successor (smallest in the right subtree)
        tmp = min_value_node(root.right)

        # Copy the inorder successor's content to this node
        root.hedge = tmp.hedge

        # Delete the inorder successor
        root.right = delete(root.right, tmp.hedge, vertex)

    return root


def find_hedge_directly_to_the_left(root, vertex):
    """ Return the half-edge immediately to the left of 'vertex'. Note: We assume such half-edge exists for a fact.
    Basically find edge with max x-coordinate of the intersection point between the hedge and the parallel to x'x
    sweep line that passes through 'vertex'.

    Keyword arguments:
    :param root : root of BST
    :param vertex : the vertex for which we need to find the half-edge immediately to the left of it
    :return: The half-edge immediately to the left of :param vertex
    """
    if root is None:
        return None
    if vertex.coordinates[0] == x_intersection_coord(root.hedge, vertex):  # 'vertex' lies on this half-edge
        return root.hedge
    elif vertex.coordinates[0] > x_intersection_coord(root.hedge, vertex):
        tmp = find_hedge_directly_to_the_left(root.right, vertex)  # Try to find closer half-edge
        if tmp is None:  # no closer half-edge
            return root.hedge
        else:
            return tmp
    # Root's half-edge is to the right so try to find the half-edge from the left subtree
    return find_hedge_directly_to_the_left(root.left, vertex)


def print_inorder(root):
    if root:
        # First recur on left child
        print_inorder(root.left)
        # then print the data of node
        print(root.hedge)
        # now recur on right child
        print_inorder(root.right)


def x_intersection_coord(hedge, vertex):
    """ Returns the x-coordinate of the intersection point between the parallel to x'x sweep line passing through
    vertex, with the hedge. Important to note that we know for a fact that this intersection point exists and is
    to the left of the vertex.

    Keyword arguments:
    :param hedge -- half-edge
    :param vertex -- Location of parallel to x'x sweep line (Sweep line intersects vertex at this point).
    :return: The x-coordinate of the intersection point between the parallel to x'x sweep line passing through
             :param vertex, with the :param hedge
    """
    orig = hedge.origin.coordinates
    dest = hedge.twin.origin.coordinates
    if orig[0] == dest[0]:
        return orig[0]
    elif orig[1] == dest[1]:
        return max(orig[0], dest[0])  # segment parallel to x'x TODO: Think about this more
    return ((dest[0] - orig[0]) * (vertex.coordinates[1] - orig[1])) / (dest[1] - orig[1]) + orig[0]


