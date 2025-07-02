from typing import Optional, List, Dict, Union, Any

from .roomcomposition import RoomComposition


class Room:
    """
        @brief A class recording all the options applicable to a single room

    """

    volume_in_m3: float
    surf_area_in_m2: float
    light_type: str
    glass_type: str

    composition: RoomComposition

    def __init__(self, volume_in_m3: float,
                 surf_area_in_m2: float,
                 light_type: str,
                 glass_type: str,
                 composition: RoomComposition):
        self.volume_in_m3 = volume_in_m3
        self.surf_area_in_m2 = surf_area_in_m2
        self.light_type = light_type
        self.glass_type = glass_type
        self.composition = composition

    def surface_area_dictionary(self):
        return self.composition.surface_area_dictionary(self.surf_area_in_m2)

