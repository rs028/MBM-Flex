import math
import unittest
from unittest.mock import Mock, patch

from multiroom_model.aperture_calculations import Fluxes
from multiroom_model.global_settings import GlobalSettings
from multiroom_model.room_chemistry import RoomChemistry
from multiroom_model.room_inchempy_evolver import RoomInchemPyEvolver
from multiroom_model.room_factory import (
    build_rooms,
    populate_room_with_emissions_file,
    populate_room_with_tvar_file,
    populate_room_with_expos_file
)


class TestApertureFlowCalculations(unittest.TestCase):


    @classmethod
    def generate_dataframe(cls):
        rooms = build_rooms("config_rooms/mr_tcon_room_params.csv")
        room_ids = list(rooms.keys())
        for i, room in rooms.items():
            populate_room_with_emissions_file(room, f"config_rooms/mr_room_emis_params_{i}.csv")
            populate_room_with_tvar_file(room, f"config_rooms/mr_tvar_room_params_{i}.csv")
            populate_room_with_expos_file(room, f"config_rooms/mr_tvar_expos_params_{i}.csv")
        global_settings = GlobalSettings(
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
        room: RoomChemistry = rooms[2]

        evolver = RoomInchemPyEvolver(room, global_settings)

        output_data, integration_times = evolver.run(
            t0=0,
            seconds_to_integrate=0,
            initial_text_file='initial_concentrations.txt'
        )
        return output_data


    @classmethod
    def setUpClass(cls):
        cls.dataframe = cls.generate_dataframe()

    
    def test_dataframe(self):
        print(self.dataframe)