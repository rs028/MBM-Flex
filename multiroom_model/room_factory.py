from .surface_composition import SurfaceComposition
from .room_chemistry import RoomChemistry
from .time_dep_value import TimeDependentValue
from.bracketed_value import TimeBracketedValue
from pandas import read_csv
import re
from typing import List, Tuple
from math import ceil


def build_rooms(csv_file: str):
    """
    Use a csv file to build a list of rooms, each populated with the properties contained in the csv file
    volume, surface area, light type, glass type and a composition of materials
    
    """
    tcon_params = read_csv(csv_file)

    nroom = len(tcon_params['room_number'])  # number of rooms (each room treated as one box)

    mrvol = tcon_params['volume_in_m3'].tolist()
    mrsurfa = tcon_params['surf_area_in_m2'].tolist()
    mrlightt = tcon_params['light_type'].tolist()
    mrglasst = tcon_params['glass_type'].tolist()

    mrsoft = tcon_params['percent_soft'].tolist()
    mrpaint = tcon_params['percent_paint'].tolist()
    mrwood = tcon_params['percent_wood'].tolist()
    mrmetal = tcon_params['percent_metal'].tolist()
    mrconcrete = tcon_params['percent_concrete'].tolist()
    mrpaper = tcon_params['percent_paper'].tolist()
    mrlino = tcon_params['percent_lino'].tolist()
    mrplastic = tcon_params['percent_plastic'].tolist()
    mrglass = tcon_params['percent_glass'].tolist()
    mrother = tcon_params['percent_other'].tolist()

    result = {}

    for i in range(nroom):
        rc = SurfaceComposition(
            soft=mrsoft[i],
            paint=mrpaint[i],
            wood=mrwood[i],
            metal=mrmetal[i],
            concrete=mrconcrete[i],
            paper=mrpaper[i],
            lino=mrlino[i],
            plastic=mrplastic[i],
            glass=mrglass[i],
            other=mrother[i])

        r = RoomChemistry(
            composition=rc,
            volume_in_m3=mrvol[i],
            surf_area_in_m2=mrsurfa[i],
            glass_type=mrglasst[i],
            light_type=mrlightt[i]
        )
        result[int(tcon_params['room_number'][i])] = r

    return result


def populate_room_with_emissions_file(room: RoomChemistry, csv_file: str):
    """
    Use a csv emissions file to populate an existing room with emissions
    """

    emis_params = read_csv(csv_file)

    time_cols = [t for t in emis_params.columns[1:]]
    species = [s for s in emis_params["species"]]

    def extract_time(s):
        match = re.search(r'\d+(\.\d+)?', s)  # matches integers or decimals
        if match:
            return float(match.group())
        else:
            raise Exception("No time detected in the collumn")

    times = [extract_time(t) for t in time_cols]
    room.emissions = {}

    for i, s in enumerate(species):
        r= []
        values = [emis_params[t][i] for t in time_cols]
        for j, v in enumerate(values):
            if (v != 0):
                r.append(tuple([times[j], times[j+1], v]))
        room.emissions[s] = TimeBracketedValue(r)



def populate_room_with_tvar_file(room: RoomChemistry, csv_file: str):
    """
    Use a csv variables file to populate an existing room with additional properties
    """
    expos_params = read_csv(csv_file)

    times = expos_params["seconds_from_midnight"]
    room.temp_in_kelvin = TimeDependentValue(list(zip(times, expos_params["temp_in_kelvin"])))
    room.rh_in_percent = TimeDependentValue(list(zip(times, expos_params["rh_in_percent"])))
    room.airchange_in_per_second = TimeDependentValue(list(zip(times, expos_params["airchange_in_per_second"])))
    room.light_switch = TimeDependentValue(list(zip(times, expos_params["light_switch"])))


def populate_room_with_expos_file(room: RoomChemistry, csv_file: str):
    """
    Use a csv exposure file to populate an existing room with numbers of children an adults
    """
    expos_params = read_csv(csv_file)

    times = expos_params["seconds_from_midnight"]
    room.n_adults = TimeDependentValue(list(zip(times, expos_params["n_adults"])))
    room.n_children = TimeDependentValue(list(zip(times, expos_params["n_children"])))
