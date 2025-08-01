import unittest
from multiroom_model.global_settings import GlobalSettings
from multiroom_model.simulation import Simulation
from multiroom_model.room_factory import (
    build_rooms,
    populate_room_with_emissions_file,
    populate_room_with_tvar_file,
    populate_room_with_expos_file
)


class TestTwoRoomSimulation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rooms = build_rooms("config_rooms/mr_tcon_room_params.csv")
        cls.room_ids = list(cls.rooms.keys())
        for i, room in cls.rooms.items():
            populate_room_with_emissions_file(room, f"config_rooms/mr_room_emis_params_{i}.csv")
            populate_room_with_tvar_file(room, f"config_rooms/mr_tvar_room_params_{i}.csv")
            populate_room_with_expos_file(room, f"config_rooms/mr_tvar_expos_params_{i}.csv")
        cls.global_settings = GlobalSettings(
            filename='chem_mech/mcm_subset.fac',
            INCHEM_additional=False,
            particles=True,
            constrained_file=None,
            output_folder=None,
            dt=1.0,
            H2O2_dep=False,
            O3_dep=False,
            custom=False,
            custom_filename=None,
            diurnal=True,
            city='London_urban',
            date='21-06-2020',
            lat=45.4,
            path=None,
            reactions_output=False
        )

    def test_2_room_simulation(self):
        rooms = [self.rooms[2], self.rooms[4]]

        simulation = Simulation(
            global_settings=self.global_settings,
            rooms=rooms,
            windows=[])

        initial_conditions = dict([(r, 'initial_concentrations.txt') for r in rooms])

        result = simulation.run(
            t0=0.0,
            t_total=25,
            t_interval=3.0,
            init_conditions=initial_conditions
        )


        print([[a for a in result[r].columns[:15]] for r in rooms])
        print([[a for a in result[r].index[:15]] for r in rooms])

        for r in rooms:

            self.assertEqual(result[r].index[0], 0.0)
            self.assertEqual(result[r].index[1], 1.0)
            self.assertEqual(result[r].index[2], 2.0)
            self.assertEqual(result[r].index[3], 3.0)

            self.assertEqual(result[r].index[4], 3.0)

            self.assertEqual(result[r].index[-3], 24.0)
            self.assertEqual(result[r].index[-2], 24.0)
            self.assertEqual(result[r].index[-1], 25.0)
            self.assertEqual(len(result[r].index), int(25/1)+1+int(25/3))
