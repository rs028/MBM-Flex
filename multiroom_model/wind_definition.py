from dataclasses import dataclass
from typing import List
from .time_dep_value import TimeDependentValue

@dataclass
class WindDefinition:
    """
        @brief A dataclass storing the information needed to determine and interpret wind speeds.
        The wind direction may be stored in radians or degrees, a bool indicates which 
        To be used we also need to know the building orientation, so that is also stored here.
    """
    building_direction: float
    wind_speed: TimeDependentValue
    wind_direction: TimeDependentValue
    in_radians: bool = True
