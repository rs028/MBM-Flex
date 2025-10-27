from typing import Any, Dict, List, Tuple, Optional
import json

from .room_chemistry import RoomChemistry
from .surface_composition import SurfaceComposition
from .time_dep_value import TimeDependentValue
from .bracketed_value import TimeBracketedValue


class RoomChemistryJSONBuilder:
    """
    Build RoomChemistry objects from JSON text or Python dictionaries.

    This builder accepts both compact array forms (historical) and
    explicit dict forms (recommended for clarity).

    Supported JSON structure (keys are optional except the constructor args):
    {
      "volume_in_m3": 100.0,
      "surf_area_in_m2": 50.0,
      "light_type": "none",
      "glass_type": "double",
      "composition": { ... },

      # time-dependent examples (either):
      "temp_in_kelvin": [[0, 293.15], [3600, 295.15]],
      "rh_in_percent": {"values": [[0, 40], [3600, 45]], "continuous": true},

      # explicit time-value dicts (clearer):
      "airchange_in_per_second": [
          {"time": 0, "value": 0.0001},
          {"t": 3600, "v": 0.0002}
      ],

      # light switch (step)
      "light_switch": {"values": [{"time": 0, "value": 0}, {"time": 36000, "value": 1}], "continuous": false},

      # emissions (bracketed triples), either compact:
      "emissions": {
          "NO2": [[0, 3600, 1.2], [7200, 10800, 0.5]],
          # or explicit objects for triples:
          "VOC": {"values": [{"start": 0, "end": 3600, "value": 0.2}]}
      },

      # people counts (time dependent)
      "n_adults": [{"time":0, "value": 1}, {"time":3600, "value":2}],
      "n_children": {"values": [[0, 0], [3600, 1]], "continuous": false}
    }

    Accepted key names in dict items:
      - time-dependent entries: keys "time" or "t" for time, "value" or "v" for value
      - bracketed entries: keys "start" or "s", "end" or "e", "value" or "v"

    The builder will convert and validate the inputs and return a RoomChemistry instance.
    """

    @staticmethod
    def from_json_text(json_text: str) -> RoomChemistry:
        data = json.loads(json_text)
        return RoomChemistryJSONBuilder.from_dict(data)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> RoomChemistry:
        # Required constructor fields
        try:
            volume = float(data["volume_in_m3"])
            surf_area = float(data["surf_area_in_m2"])
            light_type = str(data["light_type"])
            glass_type = str(data["glass_type"])
            comp_data = data["composition"]
        except KeyError as e:
            raise ValueError(f"Missing required RoomChemistry key: {e}")

        if not isinstance(comp_data, dict):
            raise ValueError("composition must be an object/dict of material percentages")

        # Build SurfaceComposition (accepts missing keys since SurfaceComposition has defaults)
        sc = SurfaceComposition(
            soft=comp_data.get("soft", 0),
            paint=comp_data.get("paint", 0),
            wood=comp_data.get("wood", 0),
            metal=comp_data.get("metal", 0),
            concrete=comp_data.get("concrete", 0),
            paper=comp_data.get("paper", 0),
            lino=comp_data.get("lino", 0),
            plastic=comp_data.get("plastic", 0),
            human=comp_data.get("human", 0),
            glass=comp_data.get("glass", 0),
            other=comp_data.get("other", None)
        )

        room = RoomChemistry(
            volume_in_m3=volume,
            surf_area_in_m2=surf_area,
            light_type=light_type,
            glass_type=glass_type,
            composition=sc
        )

        # ---- Normalizers ----
        def _normalize_time_value_list(obj: Any) -> List[Tuple[float, float]]:
            """
            Accepts:
              - list of [time, value]
              - list of {"time":t, "value":v} or {"t":..., "v":...}
              - dict {"values": ...}
            Returns list of (time, value) tuples
            """
            if obj is None:
                return []
            if isinstance(obj, dict):
                if "values" in obj:
                    source = obj["values"]
                else:
                    raise ValueError("time-dependent dict must include 'values' key")
            else:
                source = obj

            if not isinstance(source, list):
                raise ValueError("time-dependent 'values' must be a list")

            out: List[Tuple[float, float]] = []
            for i, item in enumerate(source):
                if isinstance(item, (list, tuple)):
                    if len(item) != 2:
                        raise ValueError(f"time-value pair at index {i} must have length 2 (time, value) {item}")
                    t, v = item
                elif isinstance(item, dict):
                    # accept "time" or "t", and "value" or "v"
                    if "time" in item:
                        t = item["time"]
                    elif "t" in item:
                        t = item["t"]
                    else:
                        raise ValueError(f"time-value dict at index {i} missing 'time'/'t' key {item}")
                    if "value" in item:
                        v = item["value"]
                    elif "v" in item:
                        v = item["v"]
                    else:
                        raise ValueError(f"time-value dict at index {i} missing 'value'/'v' key")
                else:
                    raise ValueError(f"Unsupported time-value item type at index {i}: {type(item)}")

                try:
                    out.append((float(t), float(v)))
                except Exception as e:
                    raise ValueError(f"Invalid numeric time/value at index {i}: {e}")
            return out

        def _normalize_bracketed_list(obj: Any) -> List[Tuple[float, float, float]]:
            """
            Accepts:
              - list of [start, end, value]
              - list of {"start":s, "end":e, "value":v} or {"s":..., "e":..., "v":...}
              - dict {"values": ...}
            Returns list of (start, end, value) tuples
            """
            if obj is None:
                return []
            if isinstance(obj, dict):
                if "values" in obj:
                    source = obj["values"]
                else:
                    raise ValueError("bracketed dict must include 'values' key")
            else:
                source = obj

            if not isinstance(source, list):
                raise ValueError("bracketed 'values' must be a list")

            out: List[Tuple[float, float, float]] = []
            for i, item in enumerate(source):
                if isinstance(item, (list, tuple)):
                    if len(item) != 3:
                        raise ValueError(f"bracketed triple at index {i} must have length 3 (start, end, value)")
                    s, e, v = item
                elif isinstance(item, dict):
                    if "start" in item:
                        s = item["start"]
                    elif "s" in item:
                        s = item["s"]
                    else:
                        raise ValueError(f"bracket dict at index {i} missing 'start'/'s' key")
                    if "end" in item:
                        e = item["end"]
                    elif "e" in item:
                        e = item["e"]
                    else:
                        raise ValueError(f"bracket dict at index {i} missing 'end'/'e' key")
                    if "value" in item:
                        v = item["value"]
                    elif "v" in item:
                        v = item["v"]
                    else:
                        raise ValueError(f"bracket dict at index {i} missing 'value'/'v' key")
                else:
                    raise ValueError(f"Unsupported bracketed item type at index {i}: {type(item)}")

                try:
                    out.append((float(s), float(e), float(v)))
                except Exception as e:
                    raise ValueError(f"Invalid numeric start/end/value at index {i}: {e}")
            return out

        # ---- Builder helpers ----
        def _make_time_dep(obj: Any, default_continuous: bool = True) -> Optional[TimeDependentValue]:
            if obj is None:
                return None
            # If obj is dict with explicit 'continuous', extract it
            if isinstance(obj, dict) and "continuous" in obj:
                continuous = bool(obj["continuous"])
            else:
                # default unless user explicitly set continuous=False on a wrapper dict
                continuous = default_continuous
            tv_pairs = _normalize_time_value_list(obj)
            if len(tv_pairs) == 0:
                raise ValueError("Time-dependent values list is empty")
            # TimeDependentValue expects list of (time, value) tuples and continuous flag
            return TimeDependentValue(tv_pairs, continuous)

        def _make_bracketed(obj: Any) -> Optional[TimeBracketedValue]:
            if obj is None:
                return None
            triples = _normalize_bracketed_list(obj)
            if len(triples) == 0:
                raise ValueError("Bracketed values list is empty")
            return TimeBracketedValue(triples)

        # Optional time-dependent fields
        if "temp_in_kelvin" in data:
            room.temp_in_kelvin = _make_time_dep(data["temp_in_kelvin"], default_continuous=True)
        if "rh_in_percent" in data:
            room.rh_in_percent = _make_time_dep(data["rh_in_percent"], default_continuous=True)
        if "airchange_in_per_second" in data:
            room.airchange_in_per_second = _make_time_dep(data["airchange_in_per_second"], default_continuous=True)
        if "light_switch" in data:
            room.light_switch = _make_time_dep(data["light_switch"], default_continuous=False)

        # Emissions: dict of species -> bracketed lists
        if "emissions" in data:
            emis = data["emissions"]
            if not isinstance(emis, dict):
                raise ValueError("emissions must be an object/dict keyed by species")
            room.emissions = {}
            for sp, val in emis.items():
                room.emissions[str(sp)] = _make_bracketed(val)

        # People counts (optional)
        if "n_adults" in data:
            room.n_adults = _make_time_dep(data["n_adults"], default_continuous=False)
        if "n_children" in data:
            room.n_children = _make_time_dep(data["n_children"], default_continuous=False)

        return room

    @staticmethod
    def parse_rooms_from_json_text(json_text: str) -> Dict[str, RoomChemistry]:
        """
        Parse JSON text that contains multiple rooms and return a dict mapping int room ids to RoomChemistry.
        Accepts:
          - top-level list of room dicts: [ {...}, {...} ]
          - top-level dict with "rooms": list or mapping
          - top-level dict mapping ids -> room dicts: { "1": {...}, "2": {...} }
        The returned dict's keys are ints if possible; otherwise consecutive integers starting at 0.
        """
        data = json.loads(json_text)
        return RoomChemistryJSONBuilder.parse_rooms_from_dict(data)

    @staticmethod
    def parse_rooms_from_json_file(json_file: str) -> Dict[str, RoomChemistry]:
        """
        Parse JSON text that contains multiple rooms and return a dict mapping int room ids to RoomChemistry.
        Accepts:
          - top-level list of room dicts: [ {...}, {...} ]
          - top-level dict with "rooms": list or mapping
          - top-level dict mapping ids -> room dicts: { "1": {...}, "2": {...} }
        The returned dict's keys are ints if possible; otherwise consecutive integers starting at 0.
        """
        with open(json_file, 'r') as file:
            data = json.loads(file.read())
        return RoomChemistryJSONBuilder.parse_rooms_from_dict(data)

    @staticmethod
    def parse_rooms_from_dict(data: Any) -> Dict[str, RoomChemistry]:
        """
        Parse a Python object (decoded JSON) containing multiple rooms.
        """
        # If data is a list -> list of room objects
        if isinstance(data, list):
            rooms_src = data
            # assign integer ids by index
            result: Dict[str, RoomChemistry] = {}
            for i, room_obj in enumerate(rooms_src):
                if not isinstance(room_obj, dict):
                    raise ValueError(f"Each room entry must be an object/dict (item {i} was {type(room_obj)})")
                result[str(i)] = RoomChemistryJSONBuilder.from_dict(room_obj)
            return result

        # If top-level has 'rooms' key, use it (can be list or mapping)
        if isinstance(data, dict) and "rooms" in data:
            rooms_val = data["rooms"]
            # if list -> behave like list case
            if isinstance(rooms_val, list):
                return RoomChemistryJSONBuilder.parse_rooms_from_dict(rooms_val)
            elif isinstance(rooms_val, dict):
                result: Dict[str, RoomChemistry] = {}
                for k, v in rooms_val.items():
                    if not isinstance(v, dict):
                        raise ValueError(f"Room entry for key {k} must be a dict")
                    result[k] = RoomChemistryJSONBuilder.from_dict(v)
                return result
            else:
                raise ValueError("'rooms' must be a list or a mapping")

        result: Dict[str, RoomChemistry] = {}
        for k, v in data.items():
            if not isinstance(v, dict):
                raise ValueError(f"Room entry for key {k} must be a dict")
            result[k] = RoomChemistryJSONBuilder.from_dict(v)
        return result
