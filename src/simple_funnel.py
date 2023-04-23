from numpy import cross, array
from scipy.spatial import distance

""" Simple Funnel Algorithm : http://digestingduck.blogspot.com/2010/03/simple-stupid-funnel-algorithm.html
Given a list of consecutive triangles (adjacent triangles share a diagonal and for each triangle there can be at most
2 neighbors - also called 'sleeve') , find the shortest path from a point in the first triangle to a point in the
last triangle. This list of triangles will be given to us as a list of faces (each face corresponds to a triangle)
in the correct order. 
"""


def find_portals(faces_path):
    bot_portals = []
    top_portals = []
    for f1, f2 in zip(faces_path[:-1], faces_path[1:]):
        hedge = find_diagonal_half_edge(f1, f2)
        bot_portals.append(hedge.origin.coordinates)
        top_portals.append(hedge.twin.origin.coordinates)
    return bot_portals, top_portals


def find_diagonal_half_edge(f1, f2):
    """ Find the half-edge that connects f1 and f2. Return the half-edge that bounds f1. We assume that a common
    edge exists (which is a diagonal).

    Keyword arguments:
    :param f1 : a Face that corresponds to a triangle
    :param f2 : a Face that corresponds to a triangle
    :returns the Hedge of their common edge that bounds f1
    """
    hedge = f1.outer_component
    while True:
        if hedge.twin.incident_face is f2:
            return hedge
        hedge = hedge.next


def ab_cross_ac(a, b, c):
    return cross(array(b) - array(a), array(c) - array(a))  # ab x ac


def funnel_shortest_path(faces_path, startpoint, endpoint, poly):
    """
    Definition of top and bot portals:
    Firstly, a pair of top_portals[i] and bot_portals[i] is a diagonal in the path of adjacent triangles. To this end,
    let's consider a path of adjacent triangles (given as faces) in the triangulated DCEL [f0, f1, f2, ... , f_n].
    This is a path from f0 -> f_n. Consider the diagonal between f_i , f_i+1. Then, the common edge is a diagonal in
    the triangulated DCEL (defined by two half-edges). Consider the half-edge of this diagonal that BOUNDS f_i.
    Then, bot_portals[i] stores the origin of this half-edge, and top_portals[i] stores the destination of this
    half-edge. (Note: No matter the orientation of the path of triangles this definition is precise. But, the names
    'top', 'bot' could be misleading because the only case where the polyline of top_portals is indeed 'on top' or
    'above' the polyline of the bot_portals is when the path of triangles go from left -> right. We advise to start
    thinking of 'top' and 'bot' as the definition above and not as the words 'top' and 'bottom')
    """
    stuck = False

    path_of_coordinates = []

    bot_portals, top_portals = find_portals(faces_path)

    top_portals.append(endpoint)
    bot_portals.append(endpoint)

    bot_curr_index, top_curr_index = 0, 0

    apex = startpoint

    path_of_coordinates.append(apex)

    while True:
        stuck = True

        if apex == endpoint:
            break
        if top_portals[top_curr_index] == endpoint or bot_portals[bot_curr_index] == endpoint:
            path_of_coordinates.append(endpoint)
            break

        bot_next = bot_portals[bot_curr_index+1]
        top_next = top_portals[top_curr_index+1]

        # This means we have to update bot_curr_index.
        if ab_cross_ac(apex, bot_portals[bot_curr_index], bot_next) >= 0:
            stuck = False

            # ab_cross_ac(apex, top_curr, bot_next) < 0 : means that the new bot_next tightens the funnel
            if bot_portals[bot_curr_index] == apex or ab_cross_ac(apex, top_portals[top_curr_index], bot_next) < 0:
                # Tighten the funnel. Move bot_curr to next
                bot_curr_index += 1
            else:
                # bot over top (we cannot move bot_curr to bot_next because the bot vector would cross and change
                # direction with the top vector) so we found a new apex. restart the scan from top_curr

                # make current top the new apex
                apex = top_portals[top_curr_index]
                path_of_coordinates.append(apex)

                # go to the last diagonal (portal) that has as top endpoint the apex.
                bot_curr_index = (top_curr_index
                                  + num_of_consecutive_elements_equal_to_start(top_portals[top_curr_index:]))
                top_curr_index = bot_curr_index+1

                # reset portal
                continue

        # This means we have to update top_curr_index.
        if ab_cross_ac(apex, top_portals[top_curr_index], top_next) <= 0:
            stuck = False

            # ab_cross_ac(apex, bot_curr, top_next) < 0 : means that the new bot_next tightens the funnel
            if top_portals[top_curr_index] == apex or ab_cross_ac(apex, bot_portals[bot_curr_index], top_next) > 0:
                # Tighten the funnel. Move top_curr to next
                top_curr_index += 1
            else:
                # top over bot (we cannot move top_curr to top_next because the top vector would cross and change
                # direction with the bot vector), so we found a new apex. restart the scan from bot_curr

                # make current bot the new apex
                apex = bot_portals[bot_curr_index]
                path_of_coordinates.append(apex)

                # go to the last diagonal (portal) that has as bot endpoint the apex.
                top_curr_index = (bot_curr_index
                                  + num_of_consecutive_elements_equal_to_start(bot_portals[bot_curr_index:]))
                bot_curr_index = top_curr_index + 1

                # reset portal
                continue

        if stuck:
            # Euclidean distance from bot_current to endpoint
            d_bot_endpoint = distance.euclidean(bot_portals[bot_curr_index], endpoint)

            # Euclidean distance from top_current to endpoint
            d_top_endpoint = distance.euclidean(top_portals[top_curr_index], endpoint)

            if d_bot_endpoint > d_top_endpoint:  # if current_top is closer to endpoint than current_bot
                # make current top the new apex
                apex = top_portals[top_curr_index]
                path_of_coordinates.append(apex)

                # go to the last diagonal (portal) that has as top endpoint the apex.
                bot_curr_index = (top_curr_index
                                  + num_of_consecutive_elements_equal_to_start(top_portals[top_curr_index:]))
                top_curr_index = bot_curr_index + 1
            else:
                # make current bot the new apex
                apex = bot_portals[bot_curr_index]
                path_of_coordinates.append(apex)

                # go to the last diagonal (portal) that has as bot endpoint the apex.
                top_curr_index = (bot_curr_index
                                  + num_of_consecutive_elements_equal_to_start(bot_portals[bot_curr_index:]))
                bot_curr_index = top_curr_index + 1
    return path_of_coordinates


def num_of_consecutive_elements_equal_to_start(lst):
    """ Returns the number of elements equal to lst[0] that are consecutive exactly after index=0
    It's easier to give examples:
    lst = [1,1,1,3,2]  :returns: 2 (because lst[0] = 1 and there are two 1s after)
    lst = [1,2,3,1,1] :returns: 0 (because lst[0] = 1 and there are no 1s afterwards)
    lst = [5,5,1,5,5] :returns: 1 (because lst[0] = 5 and there is one 5 afterwards)
    lst = [7,7,7,7,1,2] :returns: 3 (because lst[0] = 7 and there are three 7s afterwards)
    """
    count = 0
    for elem in lst[1:]:
        if elem == lst[0]:
            count += 1
        else:
            break
    return count














