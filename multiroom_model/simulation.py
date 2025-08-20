from typing import List, Tuple, Dict, Any
from .room_chemistry import RoomChemistry
from .window_chemistry import WindowChemistry
from .room_inchempy_evolver import RoomInchemPyEvolver
from .window_inchempy_evolver import WindowInchemPyEvolver
from .global_settings import GlobalSettings
import pandas as pd


class Simulation:
    """
        @brief A class which can evolve the state of species a set of rooms and windows

    """

    def __init__(self,
                 global_settings: GlobalSettings,
                 rooms: List[RoomChemistry],
                 windows: List[WindowChemistry]):

        self._global_settings = global_settings
        self._rooms = rooms
        self._windows = windows

        self._room_evolvers: List[RoomInchemPyEvolver] = [RoomInchemPyEvolver(r, self._global_settings) for r in self._rooms]
        self._window_evolvers: List[WindowInchemPyEvolver] = [WindowInchemPyEvolver() for w in self._windows]

    def run(self, init_conditions: dict, t0: float, t_total: float, t_interval: float):

        # First step

        room_results: Dict[RoomChemistry, pd.DataFrame] = dict([
            (r.room, r.run(t0=t0, seconds_to_integrate=t_interval, initial_text_file=init_conditions[r.room])[0])
            for r in self._room_evolvers])

        solved_time: float = min(r.index[-1] for i, r in room_results.items())

        cumulative_room_results: Dict[RoomChemistry, pd.DataFrame] = dict([(r, result.copy()) for r, result in room_results.items()])

        while (solved_time+t_interval <= t_total):

            window_results: Dict[WindowChemistry, Any] = [self.calculate_window_results(w, room_results) for w in self._window_evolvers]

            room_results = self.apply_window_results(room_results, window_results)

            room_results = dict([
                (r.room, r.run(t0=solved_time, seconds_to_integrate=t_interval,
                 initial_dataframe=room_results[r.room])[0])
                for r in self._room_evolvers])

            cumulative_room_results = dict([(r, pd.concat([cumulative_room_results[r], result], axis=0)) for r, result in room_results.items()])

            solved_time = min(r.index[-1] for i, r in room_results.items())

        # Final step

        if solved_time < t_total:
            window_results = [self.calculate_window_results(w, room_results) for w in self._window_evolvers]

            room_results = self.apply_window_results(room_results, window_results)

            room_results = dict([
                (r.room, r.run(t0=solved_time, seconds_to_integrate=t_total -
                 solved_time, initial_dataframe=room_results[r.room])[0])
                for r in self._room_evolvers])

            solved_time = min(r.index[-1] for i, r in room_results.items())

            cumulative_room_results = dict([(r, pd.concat([cumulative_room_results[r], result], axis=0)) for r, result in room_results.items()])

        return cumulative_room_results

    @staticmethod
    def calculate_window_results(window_evolver, room_results):
        return 0

    @staticmethod
    def apply_window_results(room_results, window_results):
        return room_results
