import unittest
from multiroom_model.global_settings import GlobalSettings
from multiroom_model.room_chemistry import RoomChemistry
from multiroom_model.room_inchempy_evolver import  RoomInchemPyEvolver
from multiroom_model.room_factory import (
    build_rooms,
    populate_room_with_emissions_file,
    populate_room_with_tvar_file,
    populate_room_with_expos_file
)

class TestRoomEvolverClass(unittest.TestCase):
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
            dt=0.2,
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

    def test_room__evolver_class(self):
        room: RoomChemistry = self.rooms[2]

        evolver  = RoomInchemPyEvolver(room, self.global_settings)

        output_data, integration_times = evolver.run(
            t0=0,
            seconds_to_integrate= 10,
            initial_text_file='initial_concentrations.txt'
        )

        
    def test_room__evolver_class_run_twice(self):
        room: RoomChemistry = self.rooms[2]

        evolver  = RoomInchemPyEvolver(room, self.global_settings)

        output_data, integration_times = evolver.run(
            t0=0,
            seconds_to_integrate= 10,
            initial_text_file='initial_concentrations.txt'
        )
        
        output_data_part2, integration_times_part2 = evolver.run(
            t0=10,
            seconds_to_integrate= 10,
            initial_dataframe=output_data
        )



