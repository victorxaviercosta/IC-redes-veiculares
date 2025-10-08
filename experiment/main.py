import ev_simulation as evs
from cs_deposition import Interpreter, LS_Methods
from sumo_setup import TraciParameters

from typing import Any
from dataclasses import dataclass


DEFAULT_OPTION: str = "both"

DEFAULT_WORKING_DIRECTORY: str = "."
DEFAULT_SUMOCFG_FILENAME: str = "ev_test_grid/ev_test.sumocfg"
DEFAULT_CSADD_FILENAME: str = "ev_test_grid/ev_test.add.xml"
DEFAULT_TRIPINFO_OUT_FILENAME = "data/trip_info.out"
DEFAULT_VIEW_FILENAME: str = "ev_test_grid/ev_test.view.xml"
DEFAULT_SUMOLOG_FILENAME: str = "data/sumo.log"

DEFAULT_INITIAL_LOG_FILENAME: str = "data/intial_run.log"
DEFAULT_VALIDATION_LOG_FILENAME: str = "data/validation_run.log"

DEFAULT_DELAY: int = 0
DEFAULT_GUI: bool = True
DEFAULT_VERBOSE: bool = True
DEFAULT_END_TIME: int = 3600

DEFAULT_DEPOSITION_METHOD: LS_Methods = LS_Methods.RANDOM
DEFAULT_MAX_STATIONS: int = 3


#from abc import ABC, abstractmethod
#from typing import override

@dataclass
class SimulationParameters:
    initial_log_filename: str = DEFAULT_INITIAL_LOG_FILENAME
    validation_log_filename: str = DEFAULT_VALIDATION_LOG_FILENAME
    add_file: str = DEFAULT_CSADD_FILENAME
    max_stations: int = DEFAULT_MAX_STATIONS
    method: LS_Methods = LS_Methods.RANDOM



class Runner():
    def __init__(self, params: TraciParameters, sim_params: SimulationParameters):
        self.params: TraciParameters = params
        self.sim_params: SimulationParameters = sim_params


    def initial_run(self) -> None:
        self.params.add_files = ""
        simulation: evs.Simulation = evs.EV_Simulation( params = self.params, sim_log_filename = self.sim_params.initial_log_filename )

        print(f"\nStarting Initial Run: (Ending at {self.params.end_time})\n")
        simulation.start()


    def validation_run(self) -> None:
        print("\nStarting CS deposition:\n")
        interpreter: Interpreter = Interpreter(max_stations=self.sim_params.max_stations)
        interpreter(log_filename=self.sim_params.initial_log_filename, output_filename=self.sim_params.add_file, method=LS_Methods(self.sim_params.method))

        self.params.add_files = self.sim_params.add_file
        simulation: evs.Simulation = evs.EV_Simulation( params = self.params, sim_log_filename = self.sim_params.validation_log_filename )

        print(f"\nStarting Validation Run: (Ending at {self.params.end_time})\n")
        simulation.start()



class TestGrid(Runner):
    def __init__(self):
        self.sim_initial_log_filename    = DEFAULT_INITIAL_LOG_FILENAME
        self.sim_validation_log_filename = DEFAULT_VALIDATION_LOG_FILENAME

        self.params: TraciParameters = TraciParameters(
            sumocfg_file       = "ev_test_grid/ev_test.sumocfg",
            add_files          = "ev_test_grid/ev_test.view.xml",
            tripinfo_out_file  = "ev_test_grid/ev_test.add.xml",
            sumo_log_file      = DEFAULT_SUMOLOG_FILENAME,
            gui_settings_files = DEFAULT_VIEW_FILENAME,
            delay      = 30,
            gui        = True,
            verbose    = True,
            end_time   = 5500
        )

    def initial_run(self):
        return super().initial_run()
    
    def validation_run(self):
        return super().validation_run()


class TestBD(Runner):
    def __init__(self):
        self.sim_initial_log_filename = DEFAULT_INITIAL_LOG_FILENAME
        self.sim_validation_log_filename = DEFAULT_VALIDATION_LOG_FILENAME

        self.params: TraciParameters = TraciParameters(
            sumocfg_file       = "2025-07-18-13-25-09/test_bd.sumocfg",
            add_files          = "2025-07-18-13-25-09/cs_test.add.xml",
            tripinfo_out_file  = DEFAULT_TRIPINFO_OUT_FILENAME,
            sumo_log_file      = DEFAULT_SUMOLOG_FILENAME,
            gui_settings_files = "2025-07-18-13-25-09/test_bd.view.xml",
            delay      = 30,
            gui        = True,
            verbose    = True,
            end_time   = 5500
        )

        self.sim_params.add_file = self.params.add_files

    def initial_run(self) -> None:
        return super().initial_run()
    
    def validation_run(self) -> None:
        return super().validation_run()


    
if __name__ == "__main__":
    p = TraciParameters()
    import argparse
    parser = argparse.ArgumentParser(description="Runs the core of the Electric vehicle Simulation")
    parser.add_argument("-opt", "--option", type = str, default = DEFAULT_OPTION, help = "Simulation's running option.\n"\
                        "- \"first\": Runs only the intial run of the simulation.\n"\
                        "- \"second\": Runs only the validation run of the simulation\n"\
                        "- \"both\": Runs both the first and validation runs of the simulation.")
    parser.add_argument("-wd", "--working-directory", default = DEFAULT_WORKING_DIRECTORY, type = str, help = "The working directory where to look for input files and store output files.")
    parser.add_argument("-scfg", "--sumocfg-file", type = str, default = DEFAULT_SUMOCFG_FILENAME, help = "SUMO's configuration file")
    parser.add_argument("-add", "--add-files", type = str, default = DEFAULT_CSADD_FILENAME, help = "CS additionals file to be created.")
    parser.add_argument("-ti", "--tripinfo-out-file", type = str, default = DEFAULT_TRIPINFO_OUT_FILENAME, help = "TripInfo output file from SUMO.")
    parser.add_argument("-sl", "--sumo-log-file", type = str, default = DEFAULT_SUMOLOG_FILENAME, help = "Filename for the logging from SUMO.")
    parser.add_argument("-gs", "--gui-settings-files", type = str, default = DEFAULT_VIEW_FILENAME, help = "Filename for the gui settings.")
    parser.add_argument("-d", "--delay", type = int, default = DEFAULT_DELAY, help = "The delay between simulation steps")
    parser.add_argument("-gui", "--gui", type = bool, default = DEFAULT_GUI, help = "Wheter the SUMO gui should be used or not.")
    parser.add_argument("-v", "--verbose", type = bool, default = DEFAULT_VERBOSE, help = "Wheter SUMO should produce verbose output or not.")
    parser.add_argument("-et", "--end-time", type = int, default = DEFAULT_END_TIME, help = "The end timestamp for the simuation. [s]")

    parser.add_argument("-il", "--initial-log", type = str, default = DEFAULT_INITIAL_LOG_FILENAME, help = "The log filename for the initial run")
    parser.add_argument("-vl", "--validation-log", type = str, default = DEFAULT_VALIDATION_LOG_FILENAME, help= "The log filename for the validation run")
    parser.add_argument("-ms", "--max-stations", type = int, default = DEFAULT_MAX_STATIONS, help = "Maximum number of stations to be added.")
    parser.add_argument("-m", "--method", type = int, default = DEFAULT_DEPOSITION_METHOD, help = "Lane Selection Method: \n"\
                        "\tAvaliable Methods: [RANDOM = 0, GREEDY = 1, ...]")

    args = parser.parse_args()

    params: TraciParameters = TraciParameters(
        sumocfg_file       = args.sumocfg_file,
        add_files          = args.add_files,
        tripinfo_out_file  = args.tripinfo_out_file,
        sumo_log_file      = args.sumo_log_file,
        gui_settings_files = args.gui_settings_files,
        delay      = args.delay,
        gui        = args.gui,
        verbose    = args.verbose,
        end_time   = args.end_time
    )

    sim_params: SimulationParameters = SimulationParameters (
        initial_log_filename = args.initial_log,
        validation_log_filename = args.validation_log,
        add_file = args.add_files,
        max_stations = args.max_stations,
        method = args.method
    )
    runner: Runner = Runner(params, sim_params)
    #runner: Runner = TestBD()

    match args.option:
        case "first":
            runner.initial_run()
        
        case "second":
            runner.validation_run()

        case "both":
            runner.initial_run()
            runner.validation_run()

        case _:
            print("Invalid running option.")