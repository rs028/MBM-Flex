from typing import List, Tuple, Dict, Any
from .room_chemistry import RoomChemistry
from .window_chemistry import WindowChemistry
from .room_inchempy_evolver import RoomInchemPyEvolver
from .window_inchempy_evolver import WindowEvolver
from .global_settings import GlobalSettings
import pandas as pd
from multiprocess import Pool


class Simulation:
    """
        @brief A class which can evolve the state of species in a set of rooms and windows

    """

    def __init__(self,
                 global_settings: GlobalSettings,
                 rooms: List[RoomChemistry],
                 windows: List[WindowChemistry],
                 processes: int = 4):

        self._processes = processes

        self._global_settings = global_settings
        self._rooms = rooms
        self._windows = windows

        with Pool(self._processes) as pool:

            args = [(r, self._global_settings) for r in self._rooms]
            self._room_evolvers: List[RoomInchemPyEvolver] = pool.starmap(self.build_room_evolver_starmap, args)

            args = [(w, self._global_settings) for w in self._windows]
            self._window_evolvers: List[WindowEvolver] = pool.starmap(self.build_window_evolver_starmap, args)

    def run(self, init_conditions: dict, t0: float, t_total: float, t_interval: float):

        with Pool(self._processes) as pool:

            # First step
            args = [(self._room_evolvers[i], t0, t_interval, init_conditions[r]) for i, r in enumerate(self._rooms)]
            room_results: List[pd.DataFrame] = pool.starmap(self.run_room_evolver_starmap_txt, args)

            solved_time: float = min(r.index[-1] for r in room_results)

            cumulative_room_results: Dict[RoomChemistry, pd.DataFrame] = dict(
                [(r, room_results[i].copy()) for i, r in enumerate(self._rooms)])

            while (solved_time+t_interval <= t_total):

                args = [(w, solved_time, room_results) for i, w in enumerate(self._window_evolvers)]
                window_results = pool.starmap(self.run_window_evolver_starmap, args)

                room_results = self.apply_window_results(room_results, window_results)

                args = [(r, solved_time, t_interval, room_results[i]) for i, r in enumerate(self._room_evolvers)]
                room_results = pool.starmap(self.run_room_evolver_starmap, args)

                cumulative_room_results = dict(
                    [(r, pd.concat([cumulative_room_results[r], room_results[i]], axis=0)) for i, r in enumerate(self._rooms)])

                solved_time = min(r.index[-1] for r in room_results)

            # Final step

            if solved_time < t_total:

                args = [(w, solved_time, room_results) for i, w in enumerate(self._window_evolvers)]
                window_results = pool.starmap(self.run_window_evolver_starmap, args)

                room_results = self.apply_window_results(room_results, window_results)

                args = [(r, solved_time, t_total-solved_time, room_results[i])
                        for i, r in enumerate(self._room_evolvers)]
                room_results = pool.starmap(self.run_room_evolver_starmap, args)

                solved_time = min(r.index[-1] for r in room_results)

                cumulative_room_results = dict(
                    [(r, pd.concat([cumulative_room_results[r], room_results[i]], axis=0)) for i, r in enumerate(self._rooms)])

        return cumulative_room_results

    @staticmethod
    def apply_window_results(room_results, window_results):
        return room_results

    @staticmethod
    def build_room_evolver_starmap(room, global_settings):
        return RoomInchemPyEvolver(room, global_settings)

    @staticmethod
    def run_room_evolver_starmap_txt(evolver, t0, t_interval, initial_text_file):
        df, _ = evolver.run(t0=t0, seconds_to_integrate=t_interval, initial_text_file=initial_text_file)
        return df

    @staticmethod
    def run_room_evolver_starmap(evolver, t0, t_interval, initial_dataframe):
        df, _ = evolver.run(t0=t0, seconds_to_integrate=t_interval, initial_dataframe=initial_dataframe)
        return df

    @staticmethod
    def build_window_evolver_starmap(window, global_settings):
        #TODO: Implement a window evolver and run it
        return WindowEvolver()

    @staticmethod
    def run_window_evolver_starmap(evolver, t0, room_results):
        #TODO: Implement a window evolver and run it
        return 0
