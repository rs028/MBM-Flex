import unittest
import json
from multiroom_model.surface_composition import SurfaceComposition
from multiroom_model.room_chemistry import RoomChemistry
from multiroom_model.time_dep_value import TimeDependentValue
from multiroom_model.bracketed_value import TimeBracketedValue
from multiroom_model.json_parser import RoomChemistryJSONBuilder



EXPLICIT_JSON = r'''
{
  "volume_in_m3": 10.0,
  "surf_area_in_m2": 29.7,
  "light_type": "Incand",
  "glass_type": "glass_C",
  "composition": {
    "soft": 0.0,
    "paint": 40.0,
    "wood": 10.0,
    "metal": 5.0,
    "concrete": 0.0,
    "paper": 0.0,
    "lino": 0.0,
    "plastic": 0.0,
    "human": 0.0,
    "glass": 45.0,
    "other": 0.0
  },
  "temp_in_kelvin": {
    "values": [
      { "time": 0, "value": 288.15 },
      { "time": 25200, "value": 288.15 },
      { "time": 50400, "value": 294.15 }
    ],
    "continuous": true
  },
  "rh_in_percent": {
    "values": [
      { "time": 0, "value": 45.0 },
      { "time": 25200, "value": 45.0 },
      { "time": 50400, "value": 40.0 }
    ],
    "continuous": true
  },
  "airchange_in_per_second": {
    "values": [
      { "time": 0, "value": 0.5 },
      { "time": 86400, "value": 1.0 }
    ],
    "continuous": true
  },
  "light_switch": {
    "values": [
      { "time": 0, "value": 0 },
      { "time": 25200, "value": 1 },
      { "time": 50400, "value": 0 }
    ],
    "continuous": false
  },
  "emissions": {
    "LIMONENE": {
      "values": [
        { "start": 46800, "end": 50400, "value": 5.00E+08 }
      ]
    },
    "BPINENE": {
      "values": [
        { "start": 46800, "end": 50400, "value": 5.00E+10 }
      ]
    }
  },
  "n_adults": {
    "values": [
      { "time": 0, "value": 0 },
      { "time": 3600, "value": 0 },
      { "time": 7200, "value": 0 },
      { "time": 10800, "value": 0 },
      { "time": 14400, "value": 0 },
      { "time": 18000, "value": 0 },
      { "time": 21600, "value": 1 },
      { "time": 25200, "value": 1 },
      { "time": 28800, "value": 1 },
      { "time": 32400, "value": 1 },
      { "time": 36000, "value": 1 },
      { "time": 39600, "value": 1 },
      { "time": 43200, "value": 1 },
      { "time": 46800, "value": 1 },
      { "time": 50400, "value": 1 },
      { "time": 54000, "value": 1 },
      { "time": 57600, "value": 1 },
      { "time": 61200, "value": 0 },
      { "time": 64800, "value": 0 },
      { "time": 68400, "value": 0 },
      { "time": 72000, "value": 0 },
      { "time": 75600, "value": 0 },
      { "time": 79200, "value": 0 },
      { "time": 82800, "value": 0 }
    ],
    "continuous": false
  },
  "n_children": {
    "values": [
      { "time": 0, "value": 0 },
      { "time": 3600, "value": 0 },
      { "time": 7200, "value": 0 },
      { "time": 10800, "value": 0 },
      { "time": 14400, "value": 0 },
      { "time": 18000, "value": 0 },
      { "time": 21600, "value": 0 },
      { "time": 25200, "value": 0 },
      { "time": 28800, "value": 0 },
      { "time": 32400, "value": 0 },
      { "time": 36000, "value": 0 },
      { "time": 39600, "value": 0 },
      { "time": 43200, "value": 0 },
      { "time": 46800, "value": 0 },
      { "time": 50400, "value": 0 },
      { "time": 54000, "value": 0 },
      { "time": 57600, "value": 0 },
      { "time": 61200, "value": 0 },
      { "time": 64800, "value": 0 },
      { "time": 68400, "value": 0 },
      { "time": 72000, "value": 0 },
      { "time": 75600, "value": 0 },
      { "time": 79200, "value": 0 },
      { "time": 82800, "value": 0 }
    ],
    "continuous": false
  }
}
'''


class TestRoomChemistryFromJson(unittest.TestCase):
    def setUp(self):
        self.room = RoomChemistryJSONBuilder.from_dict(json.loads(EXPLICIT_JSON))

    def test_basic_fields(self):
        self.assertAlmostEqual(self.room.volume_in_m3, 10.0)
        self.assertAlmostEqual(self.room.surf_area_in_m2, 29.7)
        self.assertEqual(self.room.light_type, "Incand")
        self.assertEqual(self.room.glass_type, "glass_C")

    def test_composition_explicit(self):
        comp = self.room.composition
        self.assertIsInstance(comp, SurfaceComposition)
        self.assertAlmostEqual(comp.soft, 0.0)
        self.assertAlmostEqual(comp.paint, 40.0)
        self.assertAlmostEqual(comp.wood, 10.0)
        self.assertAlmostEqual(comp.metal, 5.0)
        self.assertAlmostEqual(comp.concrete, 0.0)
        self.assertAlmostEqual(comp.paper, 0.0)
        self.assertAlmostEqual(comp.lino, 0.0)
        self.assertAlmostEqual(comp.plastic, 0.0)
        self.assertAlmostEqual(comp.human, 0.0)
        self.assertAlmostEqual(comp.glass, 45.0)
        self.assertAlmostEqual(comp.other, 0.0)

    def test_time_dependent_values(self):
        self.assertIsNotNone(self.room.temp_in_kelvin)
        self.assertIsInstance(self.room.temp_in_kelvin, TimeDependentValue)
        times = self.room.temp_in_kelvin.times()
        vals = self.room.temp_in_kelvin.values()
        self.assertEqual(len(times), 3)
        self.assertEqual(len(vals), 3)
        self.assertAlmostEqual(times[0], 0.0)
        self.assertAlmostEqual(vals[0], 288.15)

        self.assertIsNotNone(self.room.rh_in_percent)
        self.assertIsInstance(self.room.rh_in_percent, TimeDependentValue)
        self.assertEqual(len(self.room.rh_in_percent.times()), 3)

        self.assertIsNotNone(self.room.airchange_in_per_second)
        self.assertIsInstance(self.room.airchange_in_per_second, TimeDependentValue)
        self.assertEqual(len(self.room.airchange_in_per_second.times()), 2)

        self.assertIsNotNone(self.room.light_switch)
        self.assertIsInstance(self.room.light_switch, TimeDependentValue)
        self.assertEqual(len(self.room.light_switch.times()), 3)
        self.assertEqual(self.room.light_switch.values(), [0.0, 1.0, 0.0])

    def test_emissions_parsed_as_bracketed(self):
        self.assertTrue(hasattr(self.room, "emissions"))
        emis = self.room.emissions
        self.assertIn("LIMONENE", emis)
        self.assertIn("BPINENE", emis)
        self.assertIsInstance(emis["LIMONENE"], TimeBracketedValue)
        self.assertIsInstance(emis["BPINENE"], TimeBracketedValue)

        lim_vals = emis["LIMONENE"].values()
        bpin_vals = emis["BPINENE"].values()
        self.assertEqual(len(lim_vals), 1)
        self.assertEqual(len(bpin_vals), 1)

        self.assertAlmostEqual(lim_vals[0][0], 46800.0)
        self.assertAlmostEqual(lim_vals[0][1], 50400.0)
        self.assertAlmostEqual(lim_vals[0][2], 5.00e8)

        self.assertAlmostEqual(bpin_vals[0][0], 46800.0)
        self.assertAlmostEqual(bpin_vals[0][1], 50400.0)
        self.assertAlmostEqual(bpin_vals[0][2], 5.00e10)

    def test_people_counts(self):
        self.assertIsNotNone(self.room.n_adults)
        self.assertIsNotNone(self.room.n_children)
        self.assertIsInstance(self.room.n_adults, TimeDependentValue)
        self.assertIsInstance(self.room.n_children, TimeDependentValue)
        self.assertEqual(len(self.room.n_adults.times()), 24)
        self.assertEqual(len(self.room.n_children.times()), 24)

