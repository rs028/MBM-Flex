import unittest
import json
import numpy as np
from multiroom_model.surface_composition import SurfaceComposition
from multiroom_model.room_chemistry import RoomChemistry
from multiroom_model.time_dep_value import TimeDependentValue
from multiroom_model.room_factory import (
    build_rooms,
    populate_room_with_emissions_file,
    populate_room_with_tvar_file,
    populate_room_with_expos_file
)


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        # Check if the object has a __dict__ attribute (typical for most classes)
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        # Fallback to default behavior for other types
        
        if isinstance(obj, np.int64):
            return int(obj)
        
        return super().default(obj)


class TestAssembleAllRoomsFromCSV(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rooms = build_rooms("config_rooms/csv/mr_tcon_room_params.csv")
        cls.room_ids = list(cls.rooms.keys())
        for i, room in cls.rooms.items():
            populate_room_with_emissions_file(room, f"config_rooms/csv/mr_room_emis_params_{i}.csv")
            populate_room_with_tvar_file(room, f"config_rooms/csv/mr_tvar_room_params_{i}.csv")
            populate_room_with_expos_file(room, f"config_rooms/csv/mr_tvar_expos_params_{i}.csv")

    def test_number_of_rooms(self):
        self.assertEqual(len(self.rooms), 9, "Expected 9 rooms")

    def test_rooms_by_json(self):
        json_string = json.dumps(self.rooms, cls=CustomEncoder)
        print(json_string)
