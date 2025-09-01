from typing import Optional, Any
from enum import Enum

class Side(Enum):
    Front = 1
    Back = 2
    Left = 3
    Right = 4
    Upward = 5
    Downward = 6

class Window:
    def __init__(self, room1: Any, room2: Optional[Any], side_of_room_1:Side):
        self.room1 = room1
        self.room2 = room2
        self.side_of_room_1 = side_of_room_1
