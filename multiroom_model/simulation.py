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
        """
        @brief Initialize the Simulation with
        details about the building, rooms and windows.

        @param global_settings: Settings for the simulation which are independent of any one room or window.
        @param rooms: Information about the rooms.
        @param windows: Information about the windows.
        @param processes: The number of processes to use when solving.
        """

        # Number of cores to use in multiprocessing
        self._processes = processes

        self._global_settings = global_settings
        self._rooms = rooms
        self._windows = windows

        with Pool(self._processes) as pool:

            # For each room, build a room_evolver (performed in parallel)
            args = [(r, self._global_settings) for r in self._rooms]
            self._room_evolvers: List[RoomInchemPyEvolver] = pool.starmap(self.build_room_evolver_starmap, args)

            # For each window, build a window_evolver (performed in parallel)
            args = [(w, self._global_settings) for w in self._windows]
            self._window_evolvers: List[WindowEvolver] = pool.starmap(self.build_window_evolver_starmap, args)

    def run(self, init_conditions: dict, t0: float, t_total: float, t_interval: float):

        with Pool(self._processes) as pool:

            # First step 
            # using the init_conditions, perform a solve on each room (performed in parallel)
            args = [(self._room_evolvers[i], t0, t_interval, init_conditions[r]) for i, r in enumerate(self._rooms)]
            room_results: List[pd.DataFrame] = pool.starmap(self.run_room_evolver_starmap_txt, args)

            # This means the currently solved time goes up
            solved_time: float = min(r.index[-1] for r in room_results)

            # Cumulate the results for this step and others into a cumulative results dictionay
            cumulative_room_results: Dict[RoomChemistry, pd.DataFrame] = dict(
                [(r, room_results[i].copy()) for i, r in enumerate(self._rooms)])

            # Loop of incrementing time by t_interval and performing the operations
            # Stop when another increment would take it over the total
            while (solved_time+t_interval <= t_total ):

                # For each window calculate a window result  (performed in parallel)
                args = [(w, solved_time, room_results) for i, w in enumerate(self._window_evolvers)]
                window_results = pool.starmap(self.run_window_evolver_starmap, args)

                # Use the window results in adjust the room results into the input for the next iteration
                initial_condition = self.apply_window_results(room_results, window_results)

                # Use these new initial conditions and solve for the next time interval  (performed in parallel)
                args = [(r, solved_time, t_interval, initial_condition[i]) for i, r in enumerate(self._room_evolvers)]
                room_results = pool.starmap(self.run_room_evolver_starmap, args)

                # Add the new results to the cumulative result for all times
                cumulative_room_results = dict(
                    [(r, pd.concat([cumulative_room_results[r], room_results[i]], axis=0)) for i, r in enumerate(self._rooms)])

                # Increase the solved time to reflect what results we have now calculated
                solved_time = min(r.index[-1] for r in room_results)


            # Final step  if there is any time smaller than a single interval left to be solved
            if solved_time < t_total:

                # For each window calculate a window result  (performed in parallel)
                args = [(w, solved_time, room_results) for i, w in enumerate(self._window_evolvers)]
                window_results = pool.starmap(self.run_window_evolver_starmap, args)

                # Use the window results in adjust the room results into the input for the next iteration
                initial_condition = self.apply_window_results(room_results, window_results)

                # Use these new initial conditions and solve for the next time interval  (performed in parallel)
                args = [(r, solved_time, t_total-solved_time, initial_condition[i])
                        for i, r in enumerate(self._room_evolvers)]
                room_results = pool.starmap(self.run_room_evolver_starmap, args)

                # This should now have solved for times right up to time_total
                solved_time = min(r.index[-1] for r in room_results)

                # Add the new results to the cumulative result for all times
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
