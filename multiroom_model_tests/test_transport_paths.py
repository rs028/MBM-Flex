import unittest
from multiroom_model.window import Window, Side
from multiroom_model.transport_paths import TransportPath, paths_between_windows
from dataclasses import dataclass

class MockRoom:
    pass

class TestTransportPaths(unittest.TestCase):
    def setUp(self):
        self.rooms = [MockRoom() for n in range(9)]
        
    def test_one_room_one_window(self):
        #One front-side window
        windows = [
            Window(self.rooms[0], None, Side.Front)
        ]

        result = paths_between_windows(self.rooms, windows)

        self.assertEqual(len(result), 0)

    
    def test_one_room_2_windows(self):
        windows = [
            Window(self.rooms[0], None, Side.Front),
            Window(self.rooms[0], None, Side.Back),
        ]

        result = paths_between_windows(self.rooms, windows)

        self.assertEqual(len(result), 1)
        self.assertIn(Side.Front, result[0].terminus)
        self.assertIn(Side.Back, result[0].terminus)

        self.assertEqual(len(result[0].route), 2)
        self.assertIn(windows[0], result[0].route)
        self.assertIn(windows[1], result[0].route)


    def test_one_room_3_windows(self):
        windows = [
            Window(self.rooms[0], None, Side.Front),
            Window(self.rooms[0], None, Side.Back),
            Window(self.rooms[0], None, Side.Right),
        ]

        result = paths_between_windows(self.rooms, windows)

        self.assertEqual(len(result), 3)

        self.assertIn(Side.Front, result[0].terminus)
        self.assertIn(Side.Back, result[0].terminus)
        self.assertEqual(len(result[0].route), 2)
        self.assertIn(windows[0], result[0].route)
        self.assertIn(windows[1], result[0].route)
        
        self.assertIn(Side.Front, result[1].terminus)
        self.assertIn(Side.Right, result[1].terminus)
        self.assertEqual(len(result[1].route), 2)
        self.assertIn(windows[0], result[1].route)
        self.assertIn(windows[2], result[1].route)
        
        self.assertIn(Side.Back, result[2].terminus)
        self.assertIn(Side.Right, result[2].terminus)
        self.assertEqual(len(result[2].route), 2)
        self.assertIn(windows[2], result[2].route)
        self.assertIn(windows[1], result[2].route)


    def test_one_room_4_windows(self):
        windows = [
            Window(self.rooms[0], None, Side.Front),
            Window(self.rooms[0], None, Side.Back),
            Window(self.rooms[0], None, Side.Right),
            Window(self.rooms[0], None, Side.Left),
        ]

        result = paths_between_windows(self.rooms, windows)

        self.assertEqual(len(result), 6)


    
    def test_4_room_Y_shape(self):
        windows = [
            Window(self.rooms[0], None, Side.Front),
            Window(self.rooms[1], self.rooms[0], Side.Front),
            Window(self.rooms[2], self.rooms[1], Side.Front),
            Window(self.rooms[3], self.rooms[1], Side.Front),
            Window(self.rooms[2], None, Side.Back),
            Window(self.rooms[3], None, Side.Back)
        ]

        result = paths_between_windows(self.rooms, windows)

        #there should be 2 routes from front to back, each going through 4 windows
        self.assertEqual(len(result), 2)
        for r in result:
            self.assertIn(Side.Front, r.terminus)
            self.assertIn(Side.Back, r.terminus)
            self.assertEqual(len(r.route), 4)


    def test_7_room_H_shape(self):
        windows = [
            Window(self.rooms[0], None, Side.Front),
            Window(self.rooms[1], self.rooms[0], Side.Front),
            Window(self.rooms[2], self.rooms[1], Side.Front),
            Window(self.rooms[2], None, Side.Back),

            
            Window(self.rooms[3], None, Side.Front),
            Window(self.rooms[4], self.rooms[3], Side.Front),
            Window(self.rooms[5], self.rooms[4], Side.Front),
            Window(self.rooms[5], None, Side.Back),
            
            Window(self.rooms[1], self.rooms[6], Side.Right),
            Window(self.rooms[4], self.rooms[6], Side.Left),

        ]

        result = paths_between_windows(self.rooms, windows)

        #there should be 4 routes from front to back, 2 going through 4 windows, 2 going through 6 windows
        self.assertEqual(len(result), 4)
        for r in result:
            self.assertIn(Side.Front, r.terminus)
            self.assertIn(Side.Back, r.terminus)
            
        self.assertEqual(len(result[0].route), 4)
        self.assertEqual(len(result[1].route), 6)
        self.assertEqual(len(result[2].route), 4)
        self.assertEqual(len(result[3].route), 6)
