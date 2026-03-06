"""
params.py
------------------------------

Simple configuration file defining parameters for the Simulations.
"""

from .domain.types import SimOptions, LS_Methods, Volume, ChargingStation

SHOW_GRAPH: bool = False

# ===< Default Simulation parameters >===

# Running options: "init", "val" or "both"
DEFAULT_RUNNING_OPTION:     SimOptions = SimOptions.BOTH

DEFAULT_DATA_DIRECTORY:     str = "data/"
DEFAULT_LOGS_DIRECTORY:     str = "data/logs/"
DEFAULT_STATS_DIRECTORY:    str = "data/stats/"

# Input files
DEFAULT_WORKING_DIRECTORY:      str = "."
DEFAULT_SUMOCFG_FILENAME:       str = "scenarios/ev_test_grid/ev_test.sumocfg"
DEFAULT_CSADD_FILENAME:         str = "scenarios/ev_test_grid/ev_test.add.xml"
DEFAULT_VIEW_FILENAME:          str = "scenarios/real_world.view.xml"
DEFAULT_TRIPINFO_OUT_FILENAME:  str = "trip_info.out"
DEFAULT_SUMOLOG_FILENAME:       str = "sumo.log"

# Logging files
DEFAULT_INITIAL_LOG_FILENAME    : str = "initial.log"
DEFAULT_VALIDATION_LOG_FILENAME : str = "validation.log"

# Simulation's time parameters
DEFAULT_DELAY:      int = 0       # [s]
DEFAULT_END_TIME:   int = 3600    # [s]

DEFAULT_GUI_ACTION:     str = "store_true"
DEFAULT_VERBOSE_ACTION: str = "store_true"

# LS_Methods: RANDOM, GREEDY, ...
DEFAULT_DEPOSITION_METHOD: LS_Methods = LS_Methods.RANDOM

# Number of cells in the grid = DEFAULT_GRID_SIZE ** 2
DEFAULT_GRID_SIZE: int = 2


# ===< Charging Station's parameters >===
MIN_STATIONS_PER_CELL: int = 1

MAX_STATIONS: int = MIN_STATIONS_PER_CELL * DEFAULT_GRID_SIZE ** 2

DEFAULT_CS: ChargingStation = ChargingStation( 
    power = 22_000,
    efficiency = 0.95,
    capacity = 2,
    charge_delay = 5,
    length = 8
)


# ===< EV's parameters >===
ELECTRIC_VEHICLE_VTYPE: str = "electric_vehicle"  # Defined electric vehicle vtype.
VEHICLES_LENGTH: float = 5

EV_MAX_BATTERY_CAPACITY:    float = 30000   # [Wh]
LOW_BATTERY_PERCENTAGE:     float = 0.20    # [0,1]
INTIAL_BATTERY_PERCENTAGE:  float = 0.1     # [0,1] - Aplies only if RANDOM_BATTERY_START is false.

RANDOM_BATTERY_START:       bool = True
CIRCLE_ROUTE:               bool = False  # Wheter the EV's should restart their route when reaching the end.

MAX_CHARGING_STOP_DURATION: int = 1800  # [s]
MAX_VEHICLE_WAITING_TIME:   int = 10    # [s]

REROUTE_TRAVEL_DISTANCE_THRESHOLD : float = 3000 # [m]



# ===< Logging parameters >===
LOG_CHARGE_PERIOD:          int = 500    # [s]
LOG_CHARGE_LEVEL:           bool = False
LOG_STATION_DISTANCES:      bool = False
LOG_END_OF_ROUTE_REROUTE:   bool = False
LOG_PRINT:                  bool = False

LOGGING_LEVEL : Volume = Volume.ESSENTIALS

DO_SIMULATION_LOG: bool = False
