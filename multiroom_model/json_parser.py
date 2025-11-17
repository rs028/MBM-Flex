from typing import Any, Dict, List, Tuple, Optional
import pyjson5

from .room_chemistry import RoomChemistry
from .surface_composition import SurfaceComposition
from .time_dep_value import TimeDependentValue
from .bracketed_value import TimeBracketedValue
from .global_settings import GlobalSettings
from .wind_definition import WindDefinition
from .aperture import Aperture, Side


class RoomChemistryJSONBuilder:
    """
    Build RoomChemistry objects from JSON text or Python dictionaries.

    The builder will convert and validate the inputs and return a RoomChemistry instance.
    """

    @staticmethod
    def _from_any(room_obj: Any) -> RoomChemistry:
        if isinstance(room_obj, dict):
            return RoomChemistryJSONBuilder.from_dict(room_obj)
        elif isinstance(room_obj, str):
            return RoomChemistryJSONBuilder.from_json_file(room_obj)
        else:
            raise ValueError(f"Each room entry must be a dict or filename (item was {type(room_obj)})")

    @staticmethod
    def from_json_file(json_file: str) -> RoomChemistry:
        with open(json_file, 'r') as file:
            data = pyjson5.loads(file.read())
        return RoomChemistryJSONBuilder.from_dict(data)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> RoomChemistry:
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

        # Optional time-dependent fields
        if "temp_in_kelvin" in data:
            room.temp_in_kelvin = RoomChemistryJSONBuilder._make_time_dep(
                data["temp_in_kelvin"], default_continuous=True)
        if "rh_in_percent" in data:
            room.rh_in_percent = RoomChemistryJSONBuilder._make_time_dep(
                data["rh_in_percent"], default_continuous=True)
        if "airchange_in_per_second" in data:
            room.airchange_in_per_second = RoomChemistryJSONBuilder._make_time_dep(
                data["airchange_in_per_second"], default_continuous=True)
        if "light_switch" in data:
            room.light_switch = RoomChemistryJSONBuilder._make_time_dep(data["light_switch"], default_continuous=False)

        # Emissions: dict of species -> bracketed lists
        if "emissions" in data:
            emis = data["emissions"]
            if not isinstance(emis, dict):
                raise ValueError("emissions must be a dictionary keyed by species")
            room.emissions = {}
            for sp, val in emis.items():
                room.emissions[str(sp)] = RoomChemistryJSONBuilder._make_bracketed(val)

        # People counts (optional)
        if "n_adults" in data:
            room.n_adults = RoomChemistryJSONBuilder._make_time_dep(data["n_adults"], default_continuous=False)
        if "n_children" in data:
            room.n_children = RoomChemistryJSONBuilder._make_time_dep(data["n_children"], default_continuous=False)

        return room

    @staticmethod
    def parse_rooms_from_dict(data: Any) -> Dict[str, RoomChemistry]:
        """
        Parse a Python object (decoded JSON) containing multiple rooms.
        """
        # If top-level has 'rooms' key, use it
        if isinstance(data, dict) and "rooms" in data:
            rooms_val = data["rooms"]
            return RoomChemistryJSONBuilder.parse_rooms_from_dict(rooms_val)

        # If data is a list -> dict of room objects keyed on index
        if isinstance(data, list):
            return dict((i, RoomChemistryJSONBuilder._from_any(room_obj)) for i, room_obj in enumerate(data))

        # If data is a dict -> dict of room objects
        elif isinstance(data, dict):
            return dict((key, RoomChemistryJSONBuilder._from_any(room_obj)) for key, room_obj in data.items())

        else:
            raise ValueError("'rooms' must be a list or a mapping")

    @staticmethod
    def build_wind_from_dict(data: Dict[str, Any]) -> WindDefinition:

        try:
            wind_speed = RoomChemistryJSONBuilder._make_time_dep(data["wind_speed"])
            wind_direction = RoomChemistryJSONBuilder._make_time_dep(data["wind_direction"])
        except KeyError as e:
            raise ValueError(f"Missing required key for WindDefinition: {e}")

        in_radians = bool(data.get("in_radians", True))
        return WindDefinition(wind_speed, wind_direction, in_radians)

    @staticmethod
    def _normalize_time_value_list(obj: Any) -> list[tuple[float, float]]:
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

        out: list[tuple[float, float]] = []
        for i, item in enumerate(source):
            if isinstance(item, (list, tuple)):
                if len(item) != 2:
                    raise ValueError(f"time-value pair at index {i} must have length 2 (time, value) {item}")
                t, v = item
            elif isinstance(item, dict):
                t = item.get("time", item.get("t"))
                v = item.get("value", item.get("v"))
                if t is None or v is None:
                    raise ValueError(f"time/value missing in dict at index {i}")
            else:
                raise ValueError(f"Unsupported time-value item type at index {i}: {type(item)}")

            out.append((float(t), float(v)))
        return out

    @staticmethod
    def _make_time_dep(obj: Any, default_continuous: bool = True) -> Optional[TimeDependentValue]:
        if obj is None:
            return None
        continuous = bool(obj.get("continuous", default_continuous)) if isinstance(obj, dict) else default_continuous
        tv_pairs = RoomChemistryJSONBuilder._normalize_time_value_list(obj)
        if len(tv_pairs) == 0:
            raise ValueError("Time-dependent values list is empty")
        return TimeDependentValue(tv_pairs, continuous)

    @staticmethod
    def _normalize_bracketed_list(obj: Any) -> List[Tuple[float, float, float]]:
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

    @staticmethod
    def _make_bracketed(obj: Any) -> Optional[TimeBracketedValue]:
        if obj is None:
            return None
        triples = RoomChemistryJSONBuilder._normalize_bracketed_list(obj)
        if len(triples) == 0:
            raise ValueError("Bracketed values list is empty")
        return TimeBracketedValue(triples)


class GlobalSettingsJSONBuilder:
    """
    Build GlobalSettings objects from Python dictionary.
    """

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> GlobalSettings:
        """Create a GlobalSettings instance from a Python dictionary."""
        if not isinstance(data, dict):
            raise ValueError("GlobalSettings JSON root must be an object/dict")

        # Just pass through with defaults handled by the class itself
        return GlobalSettings(
            filename=data.get("filename"),
            INCHEM_additional=bool(data.get("INCHEM_additional", False)),
            particles=bool(data.get("particles", False)),
            constrained_file=data.get("constrained_file"),
            output_folder=data.get("output_folder"),
            dt=float(data.get("dt", 0.002)),
            H2O2_dep=bool(data.get("H2O2_dep", False)),
            O3_dep=bool(data.get("O3_dep", False)),
            custom=bool(data.get("custom", False)),
            custom_filename=data.get("custom_filename"),
            diurnal=bool(data.get("diurnal", False)),
            city=str(data.get("city", "London_urban")),
            date=str(data.get("date", "21-06-2020")),
            lat=float(data.get("lat", 45.4)),
            path=data.get("path"),
            reactions_output=bool(data.get("reactions_output", False)),
            building_direction_in_radians=float(data.get("building_direction_in_radians", 0.0)),
            air_density=float(data.get("air_density", 0.0)),
            upwind_pressure_coefficient=float(data.get("upwind_pressure_coefficient", 0.3)),
            downwind_pressure_coefficient=float(data.get("downwind_pressure_coefficient", -0.2)),
        )


class ApertureJSONBuilder:
    """
    Build a list of Aperture objects from python dictionary.

    Expected structure examples:

    [
      {"origin": "1", "destination": "2", "area": 1.2, "side_of_room_1": "Front"},
      {"origin": "2", "destination": "Left", "area": 0.5}
    ]

    OR compact:
    [
      ["1", "2", 1.2, "Front"],
      ["2", "Left", 0.5]
    ]
    """
    @staticmethod
    def from_dict(data: Any, rooms: Dict[str, Any]) -> List[Aperture]:
        """Parse apertures from a Python list or dict."""
        if not isinstance(data, list):
            raise ValueError("Aperture list must be a JSON array (list) of apertures")

        apertures: List[Aperture] = []
        for i, item in enumerate(data):
            try:
                ap = ApertureJSONBuilder._parse_single(item, rooms)
                apertures.append(ap)
            except Exception as e:
                raise ValueError(f"Error parsing aperture at index {i}: {e}")
        return apertures

    @staticmethod
    def _parse_single(item: Any, rooms: Dict[str, Any]) -> Aperture:
        """Parse one aperture entry."""
        # Accept both list-style and dict-style entries
        if isinstance(item, (list, tuple)):
            # format: [origin_room_id, destination_room_id_or_side, area?, side_of_room_1?]
            if len(item) < 2:
                raise ValueError("Aperture list entry must have at least 2 items (origin, destination)")
            origin_room_id = item[0]
            destination_room_id = item[1]
            area = float(item[2]) if len(item) > 2 else 0.0
            side_name = item[3] if len(item) > 3 else "Unknown"
        elif isinstance(item, dict):
            origin_room_id = item.get("origin")
            if origin_room_id is None:
                raise ValueError("Missing 'origin' field")
            destination_room_id = item.get("destination")
            if destination_room_id is None:
                raise ValueError("Missing 'destination' field")
            area = float(item.get("area", 0.0))
            side_name = item.get("side_of_room_1", "Unknown")
        else:
            raise ValueError(f"Unsupported aperture entry type: {type(item)}")

        # resolve origin_room
        if origin_room_id not in rooms:
            raise ValueError(f"Unknown origin_room ID '{origin_room_id}' in aperture")
        origin_room = rooms[origin_room_id]

        # resolve destination_room: either another room or a Side enum
        if isinstance(destination_room_id, (int, float)) or str(destination_room_id) in rooms:
            # destination_room is another room id
            destination_room = rooms[str(destination_room_id)]
        else:
            # treat as side/outside
            try:
                destination_room = Side[str(destination_room_id)]
            except KeyError:
                raise ValueError(f"Invalid destination_room/side '{destination_room_id}' (expected room key or Side name)")

        # resolve side_of_room_1
        try:
            side = Side[str(side_name)]
        except KeyError:
            side = Side.Unknown

        return Aperture(origin=origin_room, destination=destination_room, area=area, side_of_room_1=side)


class BuildingJSONParser:
    """
    Consolidated parser for a building JSON document that contains:
      - rooms
      - wind definition
      - global settings
      - apertures
    """

    @staticmethod
    def from_dicts(data: Dict[str, Any], rooms_data: Dict[str, Any]):
        # Parse rooms first
        rooms: Dict[str, RoomChemistry] = RoomChemistryJSONBuilder.parse_rooms_from_dict(rooms_data)

        # Parse wind definition
        if "wind" not in data:
            raise ValueError("Missing 'wind' section in building JSON")
        wind: WindDefinition = RoomChemistryJSONBuilder.build_wind_from_dict(data["wind"])

        # Parse global settings
        if "global_settings" not in data:
            raise ValueError("Missing 'global_settings' section in building JSON")
        global_settings: GlobalSettings = GlobalSettingsJSONBuilder.from_dict(data["global_settings"])

        # Parse apertures (needs rooms)
        if "apertures" not in data:
            apertures: List[Aperture] = []
        else:
            apertures: List[Aperture] = ApertureJSONBuilder.from_dict(data["apertures"], rooms)

        return {
            "rooms": rooms,
            "wind": wind,
            "global_settings": global_settings,
            "apertures": apertures
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        # Parse rooms first
        if "rooms" not in data:
            raise ValueError("Missing 'rooms' section in building JSON")
        return BuildingJSONParser.from_dicts(data, data["rooms"])

    @staticmethod
    def from_json_file(filename: str):
        with open(filename, "r") as f:
            data = pyjson5.load(f)
        return BuildingJSONParser.from_dict(data)

    @staticmethod
    def from_json_files(building_filename: str, rooms_files: Dict[str, Any]):
        with open(building_filename, "r") as f:
            data = pyjson5.load(f)
        return BuildingJSONParser.from_dicts(data, rooms_files)
