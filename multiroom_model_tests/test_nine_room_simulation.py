import pickle
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
        rooms = build_rooms("config_rooms/csv/mr_tcon_room_params.csv")

        for i, room in rooms.items():
            populate_room_with_emissions_file(room, f"config_rooms/csv/mr_room_emis_params_{i}.csv")
            populate_room_with_tvar_file(room, f"config_rooms/csv/mr_tvar_room_params_{i}.csv")
            populate_room_with_expos_file(room, f"config_rooms/csv/mr_tvar_expos_params_{i}.csv")

        cls.rooms = rooms.values()

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

    def test_9_room_simulation(self):
        rooms = self.rooms

        simulation = Simulation(
            global_settings=self.global_settings,
            rooms=rooms,
            apertures=[])

        initial_conditions = dict([(r, 'initial_concentrations.txt') for r in rooms])

        result = simulation.run(
            t0=0.0,
            t_total=25,
            t_interval=3.0,
            init_conditions=initial_conditions
        )

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

    @unittest.skip("Test is very long")
    def test_9_room_simulation_full_length(self):
        rooms = self.rooms

        self.global_settings.dt = 100

        simulation = Simulation(
            global_settings=self.global_settings,
            rooms=rooms,
            apertures=[])

        initial_conditions = dict([(r, 'initial_concentrations.txt') for r in rooms])

        result = simulation.run(
            t0=0.0,
            t_total=8280,
            t_interval=1500,
            init_conditions=initial_conditions
        )

        d = dict([(f"Room {i+1}", result[r]) for i, r in enumerate(rooms)])

        # pickle.dump(d, open(f"C:/temp/room_data/room_results.pkl","wb"))
