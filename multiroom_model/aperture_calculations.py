from dataclasses import dataclass
from typing import List, Union, Tuple
from .room_chemistry import RoomChemistry as Room
from .aperture import Aperture, Side
from .transport_paths import TransportPath
from .wind_definition import WindDefinition
import math

_zero_advection_tolerance: float = 1.0e-5


def transport_path_contains_room(room: Room, transport_path: TransportPath):
    for t in transport_path.route:
        if (t.aperture.room1 is room or t.aperture.room2 is room):
            return True
    return False


def is_room_cross_ventilated(room: Room, transport_paths: List[TransportPath], wind_speed: float, wind_direction: float, building_direction_in_radians: float):
    for t in transport_paths:
        if transport_path_contains_room(room, t):
            if (abs(transport_path_windspeed(t, wind_speed, wind_direction, building_direction_in_radians)) > _zero_advection_tolerance):
                return True
    return False


def room_has_outdoor_aperture(room: Room, apertures: List[Aperture]):
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


def transport_path_windspeed(transport_path: TransportPath,
                             wind_speed: float,
                             wind_direction: float,
                             building_direction_in_radians: float):

    t_p_angle = transport_path_angle_in_radians(transport_path, building_direction_in_radians)
    return wind_speed * math.cos(wind_direction-t_p_angle)


def flow_advection(io_windspd: float, oarea: float, Cd: float, Cp: float, air_density: float):
    '''
    Calculate the advection flow through an opening (door or window), given its area
    and the component of ambient wind passing through it.

    inputs:
        io_windspd = component of the wind through the aperture (m/s)
        oarea = cross section area of the aperture (m2)
        Cd_coeff = discharge coefficient of the aperture
        Cp_coeff = building pressure coefficients
        air_density = air density of dry air (kg/m3)

    returns:
        adv_flow = advection flow (m3/s)

    '''
    # turbulent flow exponent
    flow_m = 0.5

    # pressure differential (in Pa)
    P_upwind = 0.5 * air_density * (io_windspd**2) * Cp[0]
    P_downwind = 0.5 * air_density * (io_windspd**2) * Cp[1]
    delta_P = P_upwind - P_downwind

    # flow coefficient (K)
    flow_coeff = Cd * oarea

    # advection flow (in m3/s)
    adv_flow = flow_coeff * math.sqrt(2/air_density) * (delta_P**flow_m)

    print('|-------> delta_P = ', delta_P)
    print('|-------> flow_coeff = ', flow_coeff)
    print('|-------> adv_flow = ', adv_flow)

    return adv_flow


def flow_exchange(category: int):
    # TODO: this needs some calculation or something
    if category == 1:
        return 111
    elif category == 2:
        return 222
    elif category == 3:
        return 333
    elif category == 4:
        return 444
    else:
        raise Exception("unknown category")


@dataclass
class Fluxes:
    """
        @brief A dataclass to store fluxes between 2 rooms from advection and exchange fluxes
    """
    room_1: Room
    room_2: Union[Room | Side]
    from_1_to_2: float
    from_2_to_1: float


class ApertureCalculation:
    """
        @brief A class which performs the calculations of advection flow and category of an aperture

    """
    @dataclass
    class Contribution:
        path: TransportPath
        reversed: bool
        position_down_path: float

    aperture: Aperture = None
    transport_paths: List[TransportPath] = []
    is_outdoor_aperture: bool = False
    has_room_with_outdoor_aperture: bool = False
    building_direction_in_radians: float
    wind_definition: WindDefinition = None
    air_density: float = 0
    building_pressure_coefficients: Tuple[float, float] = 0, 0
    contributions: List[Contribution] = []

    def __init__(self,
                 aperture: Aperture,
                 transport_paths: List[TransportPath],
                 all_apertures: List[Aperture],
                 wind_definition: WindDefinition,
                 air_density: float = 0,
                 building_pressure_coefficients: Tuple[float, float] = (0, 0)):
        self.aperture = aperture
        self.transport_paths = transport_paths
        self.is_outdoor_aperture = (type(aperture.room2) is Side)
        self.has_room_with_outdoor_aperture = room_has_outdoor_aperture(
            aperture.room1, all_apertures) or room_has_outdoor_aperture(aperture.room2, all_apertures)
        self.building_direction_in_radians = wind_definition.building_direction \
            if wind_definition.in_radians \
            else math.radians(wind_definition.building_direction)
        self.wind_definition = wind_definition
        self.air_density = air_density
        self.building_pressure_coefficients = building_pressure_coefficients
        self.contributions = self._build_contributions(aperture, transport_paths)

    @classmethod
    def _build_contributions(cls, aperture: Aperture, transport_paths: List[TransportPath]) -> List[Contribution]:
        result = []
        for tp in transport_paths:
            for i, r in enumerate(tp.route):
                if r.aperture == aperture:
                    result.append(cls.Contribution(
                        path=tp,
                        reversed=r.reversed,
                        position_down_path=i/(len(tp.route)-1)
                    ))
        return result

    def has_advection_flow(self, wind_speed: float, wind_direction: float):
        for contribution in self.contributions:
            value = transport_path_windspeed(contribution.path, wind_speed,
                                             wind_direction, self.building_direction_in_radians)
            if abs(value) > _zero_advection_tolerance:
                return True
        return False

    def advection_flow_rate(self, wind_speed: float, wind_direction: float):
        # TODO: is it right that we just sum these contributions
        sum = 0
        for contribution in self.contributions:
            path_windspeed = transport_path_windspeed(contribution.path,
                                                      wind_speed,
                                                      wind_direction,
                                                      self.building_direction_in_radians)

            position = contribution.position_down_path if path_windspeed > 0 else 1.0-contribution.position_down_path
            apperture_windspeed = -path_windspeed if contribution.reversed else path_windspeed

            discharge_coefficient = 0.7/(1.0 + position)

            sum += flow_advection(apperture_windspeed,
                                  self.aperture.area,
                                  discharge_coefficient,
                                  self.building_pressure_coefficients,
                                  self.air_density)

        return sum

    def exchange_category(self, wind_speed: float, wind_direction: float):
        if is_room_cross_ventilated(self.aperture.room1,
                                    self.transport_paths,
                                    wind_speed,
                                    wind_direction,
                                    self.building_direction_in_radians):
            return 1
        elif is_room_cross_ventilated(self.aperture.room2,
                                      self.transport_paths,
                                      wind_speed,
                                      wind_direction,
                                      self.building_direction_in_radians):
            return 1
        elif self.is_outdoor_aperture:
            return 2
        elif self.has_room_with_outdoor_aperture:
            return 3
        else:
            return 4

    def exchange_flow_rate(self, wind_speed: float, wind_direction: float):
        category = self.exchange_category(wind_speed, wind_direction)
        return flow_exchange(category)

    def trans_matrix_contributions(self, time: float):
        wind_speed = self.wind_definition.wind_speed.value_at_time(time)
        wind_direction = self.wind_definition.wind_direction.value_at_time(time)
        wind_direction_in_radians = wind_direction if self.wind_definition.in_radians else math.radians(wind_direction)

        advection = self.advection_flow_rate(wind_speed, wind_direction_in_radians)
        if (advection > _zero_advection_tolerance):

            return Fluxes(
                room_1=self.aperture.room1,
                room_2=self.aperture.room2,
                from_1_to_2=advection,
                from_2_to_1=0
            )

        elif (advection < -_zero_advection_tolerance):

            return Fluxes(
                room_1=self.aperture.room1,
                room_2=self.aperture.room2,
                from_1_to_2=0,
                from_2_to_1=-advection
            )

        else:
            exchange = self.exchange_flow_rate(wind_speed, wind_direction_in_radians)

            return Fluxes(
                room_1=self.aperture.room1,
                room_2=self.aperture.room2,
                from_1_to_2=exchange,
                from_2_to_1=exchange
            )
