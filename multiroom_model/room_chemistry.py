from typing import Optional, List, Dict, Union, Any

from .surface_composition import SurfaceComposition
from .time_dep_value import TimeDependentValue
from .bracketed_value import TimeBracketedValue


class RoomChemistry:
    """
        @brief A class recording all the options applicable to a single room

    """

    volume_in_m3: float
    surf_area_in_m2: float
    light_type: str
    glass_type: str
    temp_in_kelvin: TimeDependentValue = None
    rh_in_percent: TimeDependentValue = None
    airchange_in_per_second: TimeDependentValue = None
    light_switch: TimeDependentValue = None
    emissions: Dict[str, TimeBracketedValue] = None
    n_adults: TimeDependentValue = None
    n_children: TimeDependentValue = None

    composition: SurfaceComposition

    def __init__(self, volume_in_m3: float,
                 surf_area_in_m2: float,
                 light_type: str,
                 glass_type: str,
                 composition: SurfaceComposition):
        self.volume_in_m3 = volume_in_m3
        self.surf_area_in_m2 = surf_area_in_m2
        self.light_type = light_type
        self.glass_type = glass_type
        self.composition = composition

    def surface_area_dictionary(self):
        return self.composition.surface_area_dictionary(self.surf_area_in_m2)
