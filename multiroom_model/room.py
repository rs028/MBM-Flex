from typing import Optional, List, Dict, Union, Any
from pandas import read_csv

from .roomcomposition import RoomComposition


class Room:
    """
        @brief A class recording all the options applicable to a single room

    """

    volume_in_m3: float
    surf_area_in_m2: float
    light_type: str
    glass_type: str

    composition: RoomComposition

    def __init__(self, volume_in_m3: float,
                 surf_area_in_m2: float,
                 light_type: str,
                 glass_type: str,
                 composition: RoomComposition):
        self.volume_in_m3 = volume_in_m3
        self.surf_area_in_m2 = surf_area_in_m2
        self.light_type = light_type
        self.glass_type = glass_type
        self.composition = composition

    def surface_area_dictionary(self):
        return self.composition.surface_area_dictionary(self.surf_area_in_m2)


def build_rooms(csv_file: str):
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
        rc = RoomComposition(
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

        r = Room(
            composition=rc,
            volume_in_m3=mrvol[i],
            surf_area_in_m2=mrsurfa[i],
            glass_type=mrglasst[i],
            light_type=mrlightt[i]
        )
        result[int(tcon_params['room_number'][i])] = r

    return result
