"""
main.py
------------------------------

...
"""

from .params import (
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

from .tools.cs_deposition import LS_Methods
from .utils.sumo_setup import TraciParameters
from .runner import SimulationParameters, Runner
from .predefitions import Predefinitions, build_predefition
from .domain.types import SimOptions, SimStatistics


def run(params: TraciParameters, sim_params: SimulationParameters, 
        predefinition: Predefinitions = Predefinitions.GRID, option: SimOptions = SimOptions.BOTH) -> SimStatistics:

    try:
        predef = Predefinitions(predefinition)
    except ValueError:
        raise ValueError(f"Invalid predefinition: {predefinition}.")

    runner: Runner = build_predefition(predef, params, sim_params)

    stats: SimStatistics = SimStatistics()

    match option:
        case SimOptions.INITIAL:
            runner.initial_run()
        
        case SimOptions.VALIDATION:
            stats = runner.validation_run()

        case SimOptions.BOTH:
            runner.initial_run()
            stats = runner.validation_run()

        case _:
            raise ValueError(f"Invalid running option: {option}.")

    return stats


import argparse
def get_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="Runs a Electric Vehicle Simulation...")
    parser.add_argument("-opt", "--option", type = int, default = DEFAULT_RUNNING_OPTION, help = "Simulation's running option.\n"
                        "   INITIAL    = 0 - Runs only the intial run of the simulation.\n"
                        "   VALIDATION = 1 - Runs only the validation run of the simulation\n"
                        "   BOTH       = 2 - Runs both the initial and validation runs of the simulation.")
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
        "       BH      = 3,\n"
        "       COLOGNE = 4"
    ))

    return parser


# === Main
def main() -> None:
    parser = get_parser()
    args = parser.parse_args()

    params: TraciParameters = TraciParameters(
        sumocfg_file       = args.sumocfg_file,
        route_files        = args.route_files,
        add_files          = args.add_files,
        tripinfo_out_file  = args.tripinfo_out_file,
        sumo_log_file      = args.sumo_log_file,
        gui_settings_files = args.gui_settings_files,
        delay              = args.delay,
        gui                = args.gui,
        verbose            = args.verbose,
        end_time           = args.end_time
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

    run(params, sim_params, args.predefinition, SimOptions(args.option))



if __name__ == "__main__":
    main()