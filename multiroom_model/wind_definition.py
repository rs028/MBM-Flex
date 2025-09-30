from dataclasses import dataclass
from .time_dep_value import TimeDependentValue

@dataclass
class WindDefinition:
    """
        @brief A dataclass storing the information needed to determine and interpret wind speeds.
        The wind direction may be stored in radians or degrees, a bool indicates whether radians are used 
    """
    wind_speed: TimeDependentValue
    wind_direction: TimeDependentValue
    in_radians: bool = True
