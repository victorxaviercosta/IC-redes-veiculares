"""
main.py
------------------------------

...
"""

import simulation.ev_simulation as evs
from tools.cs_deposition import Interpreter, LS_Methods
from utils.sumo_setup import TraciParameters
from graphs.network_graph import NetworkGraph
import domain.colors as colors

from params import (
    # === Default parameters:

    DEFAULT_RUNNING_OPTION,

    DEFAULT_WORKING_DIRECTORY,
    DEFAULT_SUMOCFG_FILENAME,
    DEFAULT_CSADD_FILENAME,
    DEFAULT_VIEW_FILENAME,
    DEFAULT_TRIPINFO_OUT_FILENAME,
    DEFAULT_SUMOLOG_FILENAME,

    DEFAULT_INITIAL_LOG_FILENAME,
    DEFAULT_VALIDATION_LOG_FILENAME,

    DEFAULT_DELAY,
    DEFAULT_END_TIME,

    DEFAULT_GUI_ACTION,
    DEFAULT_VERBOSE_ACTION,

    DEFAULT_DEPOSITION_METHOD,
    MAX_STATIONS,
    MIN_STATIONS_PER_CELL,
    DEFAULT_GRID_SIZE
)

from typing import Any
from dataclasses import dataclass
from enum import IntEnum


"""
@TODO: 
- Criar módulo de automatização do pipeline (generic_routes.py -> define_ev.py -> main.py) ...
- ...
"""


class Predefinitions(IntEnum):
    NONE    = 0,
    GRID    = 1,
    BD      = 2,
    COLOGNE = 3

# === Data Classes:

@dataclass
class SimulationParameters():
    initial_log_filename    : str = DEFAULT_INITIAL_LOG_FILENAME
    validation_log_filename : str = DEFAULT_VALIDATION_LOG_FILENAME
    add_file                : str = DEFAULT_CSADD_FILENAME
    max_stations            : int = MAX_STATIONS
    min_stations_per_cell   : str = MIN_STATIONS_PER_CELL
    method                  : LS_Methods = LS_Methods.RANDOM
    grid_size               : int = DEFAULT_GRID_SIZE


# === Simulation Controllers

class Runner():
    def __init__(self, params: TraciParameters, sim_params: SimulationParameters):
        self.params: TraciParameters = params
        self.sim_params: SimulationParameters = sim_params

        self.net_file = get_network_file(params.sumocfg_file)


    def initial_run(self) -> None:
        self.params.add_files = ""

        self.net_graph : NetworkGraph = NetworkGraph(self.net_file, {}, self.sim_params.grid_size)
        simulation: evs.Simulation = evs.EV_Simulation( params = self.params, sim_log_filename = self.sim_params.initial_log_filename, net_graph = self.net_graph )

        print(f"\n{colors.FG_GREEN}>>> Starting Initial Run:{colors.RESET} (Ending at {self.params.end_time})\n")
        simulation.start()


    def validation_run(self) -> None:
        print(f"{colors.FG_YELLOW}\nStarting CS deposition: \n{colors.RESET}")

        interpreter: Interpreter = Interpreter(log_filename=self.sim_params.initial_log_filename, output_filename=self.sim_params.add_file, 
                                               max_stations = self.sim_params.max_stations, min_stations_per_cell = self.sim_params.min_stations_per_cell)
        interpreter(net_file = self.net_file, grid_size=self.sim_params.grid_size, method=sim_params.method)
        self.net_graph : NetworkGraph = interpreter.net_graph

        self.params.add_files = self.sim_params.add_file
        simulation: evs.Simulation = evs.EV_Simulation( params = self.params, sim_log_filename = self.sim_params.validation_log_filename, net_graph = self.net_graph )

        print(f"\n{colors.FG_GREEN}>>> Starting Validation Run:{colors.RESET} (Ending at {self.params.end_time})\n")
        simulation.start()



class TestGrid(Runner):
    def __init__(self, params: TraciParameters, sim_params: SimulationParameters):
        self.sim_initial_log_filename    = DEFAULT_INITIAL_LOG_FILENAME
        self.sim_validation_log_filename = DEFAULT_VALIDATION_LOG_FILENAME

        params.sumocfg_file       = "scenarios/ev_test_grid/ev_test.sumocfg"
        params.add_files          = "scenarios/ev_test_grid/ev_test.add.xml"

        #params.delay      = 30
        params.gui        = True
        params.verbose    = True

        sim_params.add_file = params.add_files
        super().__init__(params, sim_params)

    def initial_run(self):
        return super().initial_run()
    
    def validation_run(self):
        return super().validation_run()


class TestBD(Runner):
    def __init__(self, params: TraciParameters, sim_params: SimulationParameters):
        self.sim_initial_log_filename: str = DEFAULT_INITIAL_LOG_FILENAME
        self.sim_validation_log_filename: str = DEFAULT_VALIDATION_LOG_FILENAME

        params.sumocfg_file       = "scenarios/BD/test_bd.sumocfg"
        params.add_files          = "scenarios/BD/cs_test.add.xml"

        sim_params.add_file = params.add_files
        super().__init__(params, sim_params)

    def initial_run(self) -> None:
        return super().initial_run()
    
    def validation_run(self) -> None:
        return super().validation_run()


class TestCOLOGNE(Runner):
    def __init__(self, params: TraciParameters, sim_params: SimulationParameters):
        self.sim_initial_log_filename: str = DEFAULT_INITIAL_LOG_FILENAME
        self.sim_validation_log_filename: str = DEFAULT_VALIDATION_LOG_FILENAME

        params.sumocfg_file       = "scenarios/TAPASCologne-0.32.0/sim_cologne.sumocfg"
        params.add_files          = "scenarios/TAPASCologne-0.32.0/sim_cologne_cs.add.xml"

        sim_params.add_file = params.add_files
        super().__init__(params, sim_params)

    def initial_run(self) -> None:
        return super().initial_run()
    
    def validation_run(self) -> None:
        return super().validation_run()




def get_network_file(sumocfg_file : str) -> str :
    import xml.etree.ElementTree as ET
    import os

    path = os.path.dirname(sumocfg_file)

    xml_tree : ET.ElementTree[ET.Element[str]] = ET.parse(sumocfg_file)
    xml_root : ET.Element[str] = xml_tree.getroot()

    input : ET.Element[str] = xml_root.find("input")

    return f"{path}/{input.find("net-file").get("value")}"


# === Main
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="Runs a Electric Vehicle Simulation...")
    parser.add_argument("-opt", "--option", type = str, default = DEFAULT_RUNNING_OPTION, help = "Simulation's running option.\n"\
                        "- \"init\": Runs only the intial run of the simulation.\n"\
                        "- \"val\": Runs only the validation run of the simulation\n"\
                        "- \"both\": Runs both the first and validation runs of the simulation.")
    parser.add_argument("-wd", "--working-directory", default = DEFAULT_WORKING_DIRECTORY, type = str, help = "The working directory where to look for input files and store output files.")
    parser.add_argument("-scfg", "--sumocfg-file", type = str, default = DEFAULT_SUMOCFG_FILENAME, help = "SUMO's configuration file")
    parser.add_argument("-rou", "--route-files", type = str, default = "", help = "Route files to be used in simulation.")
    parser.add_argument("-add", "--add-files", type = str, default = DEFAULT_CSADD_FILENAME, help = "CS additionals file to be created.")
    parser.add_argument("-ti", "--tripinfo-out-file", type = str, default = DEFAULT_TRIPINFO_OUT_FILENAME, help = "TripInfo output file from SUMO.")
    parser.add_argument("-sl", "--sumo-log-file", type = str, default = DEFAULT_SUMOLOG_FILENAME, help = "Filename for the logging from SUMO.")
    parser.add_argument("-gsf", "--gui-settings-files", type = str, default = DEFAULT_VIEW_FILENAME, help = "Filename for the gui settings.")
    parser.add_argument("-d", "--delay", type = int, default = DEFAULT_DELAY, help = "The delay between simulation steps")
    parser.add_argument("-gui", "--gui", action = DEFAULT_GUI_ACTION, help = "Wheter the SUMO gui should be used or not.")
    parser.add_argument("-v", "--verbose", action = DEFAULT_VERBOSE_ACTION, help = "Wheter SUMO should produce verbose output or not.")
    parser.add_argument("-et", "--end-time", type = int, default = DEFAULT_END_TIME, help = "The end timestamp for the simuation. [s]")

    parser.add_argument("-il", "--initial-log", type = str, default = DEFAULT_INITIAL_LOG_FILENAME, help = "The log filename for the initial run")
    parser.add_argument("-vl", "--validation-log", type = str, default = DEFAULT_VALIDATION_LOG_FILENAME, help= "The log filename for the validation run")
    parser.add_argument("-ms", "--max-stations", type = int, default = MAX_STATIONS, help = "Maximum number of stations to be added.")
    parser.add_argument("-msc", "--min-stations-per-cell", type = int, default = MIN_STATIONS_PER_CELL, help = "Minimum number of stations per cell.")
    parser.add_argument("-gs", "--grid-size", type = int, default = DEFAULT_GRID_SIZE, help="Grid Size (number of cells per row/collumn)")
    parser.add_argument("-m", "--method", type = int, default = DEFAULT_DEPOSITION_METHOD, help = (
        "    Avaliable Methods:\n"
        "        RANDOM         = 0,\n"
        "        GREEDY         = 1,\n"
        "        REGION_RANDOM  = 2,\n"
        "        REGION_GREEDY  = 3,\n"
        "        REGION         = 4"
    ))
    parser.add_argument("-pre", "--predefinition", type = int, default = Predefinitions.NONE, help = (
        "The selected predefinition from the ones avaliable. When this is selected, config and additionals params are ignored.\n"
        "   Avaliable predefinitions:\n"
        "       GRID    = 1,\n"
        "       BD      = 2,\n"
        "       COLOGNE = 3"
    ))

    args = parser.parse_args()

    params: TraciParameters = TraciParameters(
        sumocfg_file       = args.sumocfg_file,
        route_files        = args.route_files,
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
        min_stations_per_cell = args.min_stations_per_cell,
        method = LS_Methods(args.method),
        grid_size = args.grid_size
    )


    try:
        predef = Predefinitions(args.predefinition)
    except ValueError:
        raise ValueError(f"Invalid predefinition: {args.predefinition}")

    match predef:
        case Predefinitions.NONE:
            runner: Runner = Runner(params, sim_params)

        case Predefinitions.GRID:
            runner: Runner = TestGrid(params, sim_params)

        case Predefinitions.BD:
            runner: Runner = TestBD(params, sim_params)

        case Predefinitions.COLOGNE:
            runner: Runner = TestCOLOGNE(params, sim_params)

        case _:
            raise Exception("Invalid Predefinition.")


    match args.option:
        case "init":
            runner.initial_run()
        
        case "val":
            runner.validation_run()

        case "both":
            runner.initial_run()
            runner.validation_run()

        case _:
            print("Invalid running option.")