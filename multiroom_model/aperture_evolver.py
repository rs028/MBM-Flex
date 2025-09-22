from typing import List, Dict, Any
from .aperture import Aperture, Side
from .transport_paths import TransportPath
from .global_settings import GlobalSettings
import math


def transport_path_contains_room(room: Any, transport_path: TransportPath):
    for t in transport_path.route:
        if (t.aperture.room1 is room or t.aperture.room2 is room):
            return True
    return False


def is_room_cross_ventilated(room: Any, transport_paths: List[TransportPath], wind_speed: float, wind_direction: float, building_direction: float):
    for t in transport_paths:
        if transport_path_contains_room(room, t):
            if (transport_path_windspeed(t, wind_speed, wind_direction, building_direction) != 0.0):
                return True
    return False


def room_has_outdoor_aperture(room: Any, apertures: List[Aperture]):
    return any((a.room1 == room and type(a.room2) is Side for a in apertures))


def transport_path_angle_in_radians(transport_path: TransportPath, building_direction_in_radians: float):
    offsets = {
        (Side.Front, Side.Back): math.pi,
        (Side.Front, Side.Left): -3.0*math.pi / 4,
        (Side.Front, Side.Right): 3.0*math.pi / 4,

        (Side.Back, Side.Front): 0,
        (Side.Back, Side.Left): -math.pi / 4,
        (Side.Back, Side.Right): math.pi / 4,

        (Side.Left, Side.Front): math.pi / 4,
        (Side.Left, Side.Back): 3 * math.pi / 4,
        (Side.Left, Side.Right): math.pi/2.0,

        (Side.Right, Side.Front): -math.pi / 4,
        (Side.Right, Side.Back): -3 * math.pi / 4,
        (Side.Right, Side.Left): -math.pi/2.0,
    }
    offset = offsets.get((transport_path.start, transport_path.end))
    if offset is None:
        raise ValueError("Invalid direction transition")
    return building_direction_in_radians + offset


def transport_path_windspeed(transport_path: TransportPath, wind_speed: float, wind_direction: float, building_direction_in_radians: float):

    t_p_angle = transport_path_angle_in_radians(transport_path, building_direction_in_radians)
    return wind_speed * math.cos(wind_direction-t_p_angle)


class ApertureCalculation:
    """
        @brief A class which can model the species changes causes by an aperture

    """

    aperture: Aperture = None
    global_settings: GlobalSettings = None
    transport_paths: List[TransportPath] = []
    is_outdoor_aperture: bool = False
    has_room_with_outdoor_aperture: bool = False
    building_direction: float

    def has_advection_flow():
        pass

    def advection_flow_rate():
        pass

    def exchange_category():
        pass

    def exchange_flow_rate():
        pass

    def trans_matrix_contributions():
        pass


class ApertureEvolver:
    """
        @brief A class which can model the species changes causes by an aperture

    """

    aperture_calculator: ApertureCalculation = None