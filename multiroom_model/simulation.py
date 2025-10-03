from typing import List, Tuple, Dict, Any
import math
import re

from multiroom_model.aperture_flow_calculations import ApertureFlowCalculator
from .room_chemistry import RoomChemistry
from .aperture import Aperture, Side
from .room_inchempy_evolver import RoomInchemPyEvolver
from .aperture_calculations import ApertureCalculation
from .transport_paths import paths_through_building
from .global_settings import GlobalSettings
from .wind_definition import WindDefinition
import pandas as pd
from multiprocess import Pool


class Simulation:
    """
        @brief A class which can evolve the state of species in a set of rooms and apertures

    """

    def __init__(self,
                 global_settings: GlobalSettings,
                 rooms: List[RoomChemistry],
                 apertures: List[Aperture],
                 wind_definition: WindDefinition = None,
                 processes: int = 4):
        """
        @brief Initialize the Simulation with
        details about the building, rooms and apertures.

        @param global_settings: Settings for the simulation which are independent of any one room or aperture.
        @param rooms: Information about the rooms.
        @param apertures: Information about the apertures.
        @param processes: The number of processes to use when solving.
        """

        # Number of cores to use in multiprocessing
        self._processes = processes

        self._global_settings = global_settings
        self._rooms = rooms
        self._apertures = apertures
        self._wind_definition = wind_definition

        with Pool(self._processes) as pool:

            # For each room, build a room_evolver (performed in parallel)
            args = [(r, self._global_settings) for r in self._rooms]
            self._room_evolvers: List[RoomInchemPyEvolver] = pool.starmap(self.build_room_evolver_starmap, args)

            # For each aperture, build a ApertureCalculation (performed in parallel)
            transport_paths = paths_through_building(self._rooms, self._apertures)
            args = [(w, transport_paths, self._apertures, self._rooms, self._global_settings) for w in self._apertures]
            self._aperture_calculators: List[ApertureCalculation] = pool.starmap(
                self.build_aperture_calculator_starmap, args)

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
            while (solved_time+t_interval <= t_total):

                # For each aperture  calculate a aperture result  (performed in parallel)
                wind_speed = self._wind_definition.wind_speed.value_at_time(solved_time)
                wind_direction = self._wind_definition.wind_direction.value_at_time(solved_time)
                wind_direction_in_radians = wind_direction if self._wind_definition.in_radians else math.radians(
                    wind_direction)
                args = [(w, wind_speed, wind_direction_in_radians, t_interval, room_results, solved_time)
                        for i, w in enumerate(self._aperture_calculators)]
                aperture_results = pool.starmap(self.run_aperture_calculation_starmap, args)

                # Use the aperture results in adjust the room results into the input for the next iteration
                initial_condition = self.apply_aperture_results(room_results, aperture_results, solved_time)

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

                # For each aperture calculate a aperture result  (performed in parallel)
                wind_speed = self._wind_definition.wind_speed.value_at_time(solved_time)
                wind_direction = self._wind_definition.wind_direction.value_at_time(solved_time)
                wind_direction_in_radians = wind_direction if self._wind_definition.in_radians else math.radians(
                    wind_direction)
                args = [(w, wind_speed, wind_direction_in_radians, t_interval, room_results, solved_time)
                        for i, w in enumerate(self._aperture_calculators)]
                aperture_results = pool.starmap(self.run_aperture_calculation_starmap, args)

                # Use the aperture results in adjust the room results into the input for the next iteration
                initial_condition = self.apply_aperture_results(room_results, aperture_results, solved_time)

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
    def apply_aperture_results(room_results, aperture_results, solved_time):
        result = [result.loc[[solved_time], :].astype(float) for result in room_results]
        for room_1_concentration_change, room_2_concentration_change, room1_index, room2_index in aperture_results:
            is_outdoor_aperture = type(room2_index) == Side
            if (is_outdoor_aperture):
                new_room_1_value = result[room1_index].loc[solved_time, :].add(
                    room_1_concentration_change, fill_value=0.0)
                result[room1_index].loc[solved_time, :] = new_room_1_value
            else:
                new_room_1_value = result[room1_index].loc[solved_time, :].add(
                    room_1_concentration_change, fill_value=0.0)
                result[room1_index].loc[solved_time, :] = new_room_1_value
                new_room_2_value = result[room2_index].loc[solved_time, :].add(
                    room_2_concentration_change, fill_value=0.0)
                result[room2_index].loc[solved_time, :] = new_room_2_value
        return result

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
    def build_aperture_calculator_starmap(aperture, transport_paths, apertures, rooms, global_settings):
        room_1_index = rooms.index(aperture.room1)
        room_2_index = aperture.room2 if type(aperture.room2) == Side else rooms.index(aperture.room2)
        room_1_volume = aperture.room1.volume_in_m3
        room_2_volume = 0 if type(aperture.room2) == Side else aperture.room2.volume_in_m3
        return ApertureCalculation(aperture,
                                   transport_paths,
                                   apertures,
                                   global_settings.building_direction_in_radians,
                                   global_settings.air_density,
                                   (global_settings.upwind_pressure_coefficient,
                                    global_settings.downwind_pressure_coefficient)), room_1_index, room_2_index, room_1_volume, room_2_volume

    @staticmethod
    def run_aperture_calculation_starmap(aperture_calculator_data, wind_speed, wind_direction, delta_time, room_results, solved_time):
        aperture_calculator, room1_index, room2_index, room_1_volume, room_2_volume = aperture_calculator_data
        flux = aperture_calculator.trans_matrix_contributions(wind_speed, wind_direction)
        calculator = ApertureFlowCalculator(room_results[room1_index].columns)
        is_outdoor_aperture = type(room2_index) == Side
        if (is_outdoor_aperture):
            room1_concentration = room_results[room1_index].loc[solved_time, :]
            room_1_concentration_change = calculator.outdoor_concentration_changes(
                flux,
                delta_time,
                room1_concentration,
                room_1_volume)
            return room_1_concentration_change, None, room1_index, room2_index
        else:
            room1_concentration = room_results[room1_index].loc[solved_time, :]
            room2_concentration = room_results[room2_index].loc[solved_time, :]
            room_1_concentration_change, room_2_concentration_change = calculator.concentration_changes(
                flux,
                delta_time,
                room1_concentration,
                room2_concentration,
                room_1_volume,
                room_2_volume)
            return room_1_concentration_change, room_2_concentration_change, room1_index, room2_index
