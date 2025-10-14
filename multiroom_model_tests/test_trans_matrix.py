import unittest
import math
from multiroom_model.aperture_factory import build_apertures_from_double_definition, build_wind_definition
from multiroom_model.room_factory import (
    build_rooms,
    populate_room_with_emissions_file,
    populate_room_with_tvar_file,
    populate_room_with_expos_file,
    TimeDependentValue
)
from multiroom_model.aperture_calculations import Side
from multiroom_model.simulation import Simulation, Aperture, WindDefinition
from multiroom_model.global_settings import GlobalSettings
from multiroom_model.aperture_calculations import flow_advection
import numpy as np


class TestTransMatrix(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rooms = build_rooms("config_rooms/mr_tcon_room_params.csv")

        for i, room in cls.rooms.items():
            populate_room_with_emissions_file(room, f"config_rooms/mr_room_emis_params_{i}.csv")
            populate_room_with_tvar_file(room, f"config_rooms/mr_tvar_room_params_{i}.csv")
            populate_room_with_expos_file(room, f"config_rooms/mr_tvar_expos_params_{i}.csv")

        cls.apertures = build_apertures_from_double_definition("config_rooms/mr_tcon_building.csv", cls.rooms)
        cls.wind_definition = build_wind_definition("config_rooms/mr_tvar_wind_params.csv")
        cls.rooms = list(cls.rooms.values())

        ambient_press = 1013.0   # ambient pressure (mbar) is assumed to be constant, and is the same in all rooms
        ambient_temp = 293.0     # ambient temperature (K) is assumed to be constant

        rho = (100*ambient_press) / (287.050 * ambient_temp)  # ambient air density (assuming dry air), in kg/m3

        cls.global_settings = GlobalSettings(
            filename='chem_mech/mcm_subset.fac',
            INCHEM_additional=False,
            particles=True,
            constrained_file=None,
            output_folder=None,
            dt=1,
            H2O2_dep=False,
            O3_dep=False,
            custom=False,
            custom_filename=None,
            diurnal=True,
            city='London_urban',
            date='21-06-2020',
            lat=45.4,
            path=None,
            reactions_output=False,
            building_direction_in_radians=math.radians(180),
            air_density=rho,
            upwind_pressure_coefficient=0.3,
            downwind_pressure_coefficient=-0.2
        )

    def flow_advection(self, wind_speed, area, position):
        return flow_advection(wind_speed,
                              area,
                              0.7/(1+position),
                              (self.global_settings.upwind_pressure_coefficient,
                               self.global_settings.downwind_pressure_coefficient),
                              self.global_settings.air_density)

    
    def test_trans_matrix(self):

        simulation = Simulation(self.global_settings, self.rooms, self.apertures, self.wind_definition)

        for time in (0, 46805, 82800, ):
            matrix = simulation.trans_matrix(time)

            print(np.transpose(matrix.nonzero()))
            print(len(np.transpose(matrix.nonzero())))
            print(len(self.apertures))

            self.assertEqual(matrix.shape, (10,10))

            self.assertFalse(np.isnan(matrix.max()))
            self.assertFalse(np.isnan(matrix.min()))
            print(matrix)

    def test_one_room(self):

        rooms = [self.rooms[0],]

        apertures = [
            Aperture(self.rooms[0], Side.Front, 10),
            Aperture(self.rooms[0], Side.Back, 10),
        ]

        wind_definition = WindDefinition(TimeDependentValue([(0, 1),], True), TimeDependentValue([(0, 0),], True))

        simulation = Simulation(self.global_settings, rooms, apertures, wind_definition)

        matrix = simulation.trans_matrix(0)

        print(matrix)
        self.assertEqual(matrix.shape, (2,2))

        self.assertEqual(matrix[0, 0], 0)
        self.assertEqual(matrix[1, 1], 0)

        self.assertGreater(matrix[0, 1], 0)
        self.assertGreater(matrix[1, 0], 0)

        self.assertEqual(matrix[0, 1], self.flow_advection(1, 10, 0))
        self.assertEqual(matrix[1, 0], self.flow_advection(1, 10, 1))
