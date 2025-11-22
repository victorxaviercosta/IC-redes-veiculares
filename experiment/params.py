"""
params.py
-------------

Simple configuration file defining parameters for the Simulations.
"""

from domain.types import LS_Methods, Volume, ChargingStation

# === Default Simulation Parameters:

# Running options: "init", "val" or "both"
DEFAULT_RUNNING_OPTION : str = "both"

# Input files
DEFAULT_WORKING_DIRECTORY       : str = "."
DEFAULT_SUMOCFG_FILENAME        : str = "scenarios/ev_test_grid/ev_test.sumocfg"
DEFAULT_CSADD_FILENAME          : str = "scenarios/ev_test_grid/ev_test.add.xml"
DEFAULT_VIEW_FILENAME           : str = "scenarios/real_world.view.xml"
DEFAULT_TRIPINFO_OUT_FILENAME   : str = "data/trip_info.out"
DEFAULT_SUMOLOG_FILENAME        : str = "data/sumo.log"

# Logging files
DEFAULT_INITIAL_LOG_FILENAME    : str = "data/intial_run.log"
DEFAULT_VALIDATION_LOG_FILENAME : str = "data/validation_run.log"

# Simulation's time parameters
DEFAULT_DELAY       : int = 0
DEFAULT_END_TIME    : int = 3600

DEFAULT_GUI_ACTION      : str = "store_true"
DEFAULT_VERBOSE_ACTION  : str = "store_true"

# LS_Methods: RANDOM, GREEDY, ...
DEFAULT_DEPOSITION_METHOD: LS_Methods = LS_Methods.RANDOM



# ===< Charging Station's parameters >===
MAX_STATIONS : int = 6

DEFAULT_CS: ChargingStation = ChargingStation( 
    power = 22_000,
    efficiency = 0.95,
    capacity = 2,
    charge_delay = 5,
    length = 5
)


# ===< EV's parameters >===
ELECTRIC_VEHICLE_VTYPE : str = "electric_vehicle"            # Defined electric vehicle vtype.
VEHICLES_LENGTH : float = 5

EV_MAX_BATTERY_CAPACITY     : float = 30000   # [Wh]
LOW_BATTERY_PERCENTAGE      : float = 0.25    # [0,1]
INTIAL_BATTERY_PERCENTAGE   : float = 0.1     # [0,1]

RANDOM_BATTERY_START        : bool = False
CIRCLE_ROUTE                : bool = False

MAX_CHARGING_STOP_DURATION  : int = 1800  # [s]
MAX_VEHICLE_WAITING_TIME    : int = 10    # [s]

REROUTE_TRAVEL_DISTANCE_THRESHOLD : float = float("inf")



# ===< Logging parameters >===
LOG_CHARGE_PERIOD        : int = 500 # [s]
LOG_CHARGE_LEVEL         : bool = False
LOG_STATION_DISTANCES    : bool = False
LOG_END_OF_ROUTE_REROUTE : bool = False

LOGGING_LEVEL: Volume = Volume.ESSENTIALS