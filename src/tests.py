"""
tests.py
------------------------------

...
"""

import numpy as np
from dataclasses import dataclass

from predefitions import Predefinitions
from domain.types import LS_Methods, SimStatistics
from utils.sumo_setup import TraciParameters
from runner import SimulationParameters
from main import run

from params import (
    DEFAULT_VIEW_FILENAME,
    DEFAULT_TRIPINFO_OUT_FILENAME,
    DEFAULT_SUMOLOG_FILENAME,

    DEFAULT_INITIAL_LOG_FILENAME,
    DEFAULT_VALIDATION_LOG_FILENAME
)


METHOD_NAME: dict[LS_Methods, str] = {
    LS_Methods.RANDOM: "random",
    LS_Methods.GREEDY: "greedy",
    LS_Methods.REGION_RANDOM: "region_random",
    LS_Methods.REGION_GREEDY: "region_greedy"
}

# === Test Parameters

TESTS_METHODS: list[LS_Methods] = [LS_Methods.RANDOM, 
                                   LS_Methods.GREEDY, 
                                   LS_Methods.REGION_RANDOM, 
                                   LS_Methods.REGION_GREEDY]
TESTS_PERCENTAGES: np.ndarray = np.array([1, 5, 10, 15, 20], dtype=int)
TESTS_QTT_STATIONS: np.ndarray = np.array([2, 5, 10, 15, 20], dtype=int)

# TESTS_PERCENTAGES: np.ndarray = np.array([1, 10], dtype=int)
# TESTS_QTT_STATIONS: np.ndarray = np.array([5, 20], dtype=int)
# TESTS_METHODS: list[LS_Methods] = [LS_Methods.REGION_RANDOM, 
#                                    LS_Methods.REGION_GREEDY]

TESTS_SCENARIO_WORKING_DIRECTORY: str = "scenarios/BH/"
TESTS_SCENARIO: Predefinitions = Predefinitions.BH
TESTS_END_TIME: int = 1000

TESTS_STATION_CAPACITY: int = 2
TESTS_GRID_SIZE: int = 3
TESTS_MIN_STATIONS_PER_CELL: np.ndarray = np.ceil(TESTS_QTT_STATIONS / TESTS_GRID_SIZE**2).astype(int)

TESTS_QTT_ROUTE_SAMPLES: int = 2

TESTS_DATA_DIRECTORY: str = "data/tests/"

    

class EVSimulationTests():
    def __init__(self):
        self.params: TraciParameters = TraciParameters(
            tripinfo_out_file  = DEFAULT_TRIPINFO_OUT_FILENAME,
            sumo_log_file      = DEFAULT_SUMOLOG_FILENAME,
            gui_settings_files = DEFAULT_VIEW_FILENAME,
            delay              = 0,
            gui                = False,
            verbose            = False,
            end_time           = TESTS_END_TIME
        )

        self.sim_params: SimulationParameters = SimulationParameters (
            grid_size = TESTS_GRID_SIZE
        )

        # {percentage: {qtt_statitions: stats}}
        self.stats: dict[int, dict[int, SimStatistics]] = {}

    
    def run_initials(self):
        # Initial Runs
        for percentage in TESTS_PERCENTAGES:
            for j in range(TESTS_QTT_ROUTE_SAMPLES):
                self.sim_params.initial_log_filename = f"{percentage}_{j}_{DEFAULT_INITIAL_LOG_FILENAME}"
                stats = run(self.params, self.sim_params, TESTS_SCENARIO, "init")

    def run_tests(self):
        """ 
        For each method: 5 percentages
        For each percentage: 5 station quantities
        For each quantite: 5 route sampels

        Total 125 simulations per method.

        4 Methods: 500 simulations in total.
        """
        
        # Validation_runs
        for method in TESTS_METHODS:

            for percentage in TESTS_PERCENTAGES:
                self.stats[percentage] = {}

                for i, qtt in enumerate(TESTS_QTT_STATIONS):
                    self.sim_params.method = method
                    self.sim_params.max_stations = qtt
                    self.sim_params.min_stations_per_cell = TESTS_MIN_STATIONS_PER_CELL[i]

                    self.stats[percentage][qtt] = SimStatistics()
                    for j in range(TESTS_QTT_ROUTE_SAMPLES):
                        self.sim_params.initial_log_filename = f"{percentage}_{j}_{DEFAULT_INITIAL_LOG_FILENAME}"
                        self.sim_params.validation_log_filename = f"{METHOD_NAME[method]}_{percentage}_{qtt}_{j}_{DEFAULT_VALIDATION_LOG_FILENAME}"
                        self.params.route_files = f"{TESTS_SCENARIO_WORKING_DIRECTORY}routes_{percentage}_{j}.rou.xml"

                        print(f"\n{percentage}% - Qtt: {qtt} - it: {j}")
                        stats = run(self.params, self.sim_params, TESTS_SCENARIO, "val")
                        self.stats[percentage][qtt].average_no_station_time += stats.average_no_station_time
                        self.stats[percentage][qtt].average_travel_distance += stats.average_travel_distance

                    self.stats[percentage][qtt].average_no_station_time /= TESTS_QTT_ROUTE_SAMPLES
                    self.stats[percentage][qtt].average_travel_distance /= TESTS_QTT_ROUTE_SAMPLES
            
            self.write_stats(f"{TESTS_DATA_DIRECTORY}{METHOD_NAME[method]}.data")


    def write_stats(self, filepath: str) -> None:
        with open(filepath, "w") as file:
            for percentage, data in self.stats.items():
                file.write(f"{percentage}%\n")

                for qtt, stats in data.items():
                    file.write(f"{qtt}: {stats.average_no_station_time} {stats.average_travel_distance}\n")
                
                file.write("\n")


if __name__ == "__main__":
    tester: EVSimulationTests = EVSimulationTests()
    #tester.run_initials()
    tester.run_tests()