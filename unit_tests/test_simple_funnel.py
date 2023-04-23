import unittest
from unittest import mock
from src.simple_funnel import funnel_shortest_path


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.top_portals = [
            (-16.44, 11.03), (-16.44, 11.03), (-17.1, 9.13), (-17.1, 9.13), (-17.1, 9.13), (-15.48, 9.55),
            (-14.36, 9.25), (-14.36, 9.25), (-14.36, 9.25), (-12.82, 9.65), (-12.82, 9.65), (-12.82, 9.65),
            (-12.82, 9.65), (-12.96, 11.31)
        ]

        self.bot_portals = [
            (-18.78, 10.43), (-18.84, 9.05), (-18.84, 9.05), (-17.68, 7.63), (-15.96, 7.15), (-15.96, 7.15),
            (-15.96, 7.15), (-14.26, 7.63), (-12.24, 7.35), (-12.24, 7.35), (-9.76, 8.97), (-9.66, 10.57),
            (-11.3, 12.79), (-11.3, 12.79)
        ]

        self.p1_answer = [(-17.78, 11.23), (-17.1, 9.13), (-14.36, 9.25), (-12.82, 9.65), (-12.68, 13.13)]
        self.p2_answer = [(-17.72, 10.96), (-17.1, 9.13), (-14.36, 9.25), (-12.82, 9.65), (-12.4559, 12.52711)]
        self.p3_answer = [(-17.33132, 10.97701), (-17.1, 9.13), (-14.36, 9.25), (-12.82, 9.65), (-11.82962, 12.69731)]

        self.reverse_dir_bot_portals = [
            (-12.96, 11.31), (-12.82, 9.65), (-12.82, 9.65), (-12.82, 9.65), (-12.82, 9.65), (-14.36, 9.25),
            (-14.36, 9.25), (-14.36, 9.25), (-15.48, 9.55), (-17.1, 9.13), (-17.1, 9.13), (-17.1, 9.13),
            (-16.44, 11.03), (-16.44, 11.03)
        ]

        self.reverse_dir_top_portals = [
            (-11.3, 12.79), (-11.3, 12.79), (-9.66, 10.57), (-9.76, 8.97), (-12.24, 7.35), (-12.24, 7.35),
            (-14.26, 7.63), (-15.96, 7.15), (-15.96, 7.15), (-15.96, 7.15), (-17.68, 7.63), (-18.84, 9.05),
            (-18.84, 9.05), (-18.78, 10.43)
        ]

        self.p4_reverse_answer = [(-12.68, 13.13), (-12.82, 9.65), (-14.36, 9.25), (-17.1, 9.13), (-17.78, 11.23)]
        self.p5_reverse_answer = [(-11.82962, 12.69731), (-12.82, 9.65), (-14.36, 9.25), (-17.1, 9.13), (-17.33132, 10.97701)]
        self.p6_reverse_answer = [(-12.75468, 11.75601), (-12.82, 9.65), (-14.36, 9.25), (-17.1, 9.13),
                                  (-18.17524, 10.7498)]

    def test_funnel_shortest_path1(self):
        with mock.patch('simple_funnel.find_portals', self.mocked_find_portals):
            p1 = funnel_shortest_path(None, (-17.78, 11.23), (-12.68, 13.13))
        self.assertListEqual(p1, self.p1_answer)

    def test_funnel_shortest_path2(self):
        with mock.patch('simple_funnel.find_portals', self.mocked_find_portals):
            p2 = funnel_shortest_path(None, (-17.72, 10.96), (-12.4559, 12.52711))
        self.assertListEqual(p2, self.p2_answer)

    def test_funnel_shortest_path3(self):
        with mock.patch('simple_funnel.find_portals', self.mocked_find_portals):
            p3 = funnel_shortest_path(None, (-17.33132, 10.97701), (-11.82962, 12.69731))
        self.assertListEqual(p3, self.p3_answer)

    def test_funnel_shortest_path4(self):
        with mock.patch('simple_funnel.find_portals', self.mocked_find_portals_reversed):
            p4 = funnel_shortest_path(None, (-12.68, 13.13), (-17.78, 11.23))
        self.assertListEqual(p4, self.p4_reverse_answer)

    def test_funnel_shortest_path5(self):
        with mock.patch('simple_funnel.find_portals', self.mocked_find_portals_reversed):
            p5 = funnel_shortest_path(None, (-11.82962, 12.69731), (-17.33132, 10.97701))
        self.assertListEqual(p5, self.p5_reverse_answer)

    def test_funnel_shortest_path6(self):
        with mock.patch('simple_funnel.find_portals', self.mocked_find_portals_reversed):
            p6 = funnel_shortest_path(None, (-12.75468, 11.75601), (-18.17524, 10.7498))
        self.assertListEqual(p6, self.p6_reverse_answer)

    def mocked_find_portals(self, x):
        return self.bot_portals, self.top_portals

    def mocked_find_portals_reversed(self, x):
        return self.reverse_dir_bot_portals, self.reverse_dir_top_portals


if __name__ == '__main__':
    unittest.main()
