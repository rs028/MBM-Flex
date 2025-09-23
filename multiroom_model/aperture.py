from typing import Union, Any
from enum import Enum
from .room_chemistry import RoomChemistry as Room


class Side(Enum):
    """
        @brief A side of of the building or a side of a room on which an aperture is situated.
    """

    Unknown = 0
    Front = 1
    Back = 2
    Left = 3
    Right = 4
    Upward = 5
    Downward = 6


class Aperture:
    """
        @brief An aperture either between 2 rooms, or from the room to the outside
        May include the side of the room where the aperture is situated
    """

    def __init__(self, room1: Room, room2: Union[Room | Side], area: float = 0, side_of_room_1: Side = Side.Unknown):
        self.room1 = room1
        self.room2 = room2
        self.side_of_room_1 = side_of_room_1
        self.area = area
