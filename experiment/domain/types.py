"""
domain/data_types.py
------------------------------

...
"""

from dataclasses import dataclass
from enum import Enum


# ===< Lane Selection Methods >===
class LS_Methods(Enum):
    RANDOM = 0
    GREEDY = 1
    OTHER  = 2

# ===< Volume levels >===
class Volume(Enum):
    ESSENTIALS = 0
    UTILS      = 1
    SPECIFICS  = 2
    ALL        = 3

@dataclass
class VehState:
    """ Data Class to store the current state of a vehicle """
    origin  : str
    destiny : str
    low_battery_start_time : float = 0.0
    low_battery_start_dist : float = 0.0

    #avg_low_battery_time: float


@dataclass
class Reroute:
    """ Data Class for representing a reroute """
    veh_id: str
    original_destiny: str
    new_destiny: str


@dataclass
class LaneData:
    """ Data Class for storing information about a Lane """
    lane_id: str
    lane_length: float
    visits_count: int


@dataclass(frozen = True)
class ChargingStation():
    """ A class defining a Charging Station and utility methods. """

    power       : float # [W]
    efficiency  : float # [0,1]
    capacity    : int   # [u] (units, maximum number of vehicles that can charge simultaniosly)
    charge_delay: float # [s] (measured in Simulation's step-length, 1 second by default)
    length      : float # [m]

    @staticmethod
    def get_pa_id(cs_id: str) -> str:
        return cs_id.replace("cs_", "pa_", 1)
    

@dataclass
class SimStatictics():
    """ Data class for storing Simulation Statistic Mesurements """
    
    average_no_station_time : float = 0 # [s]
    average_travel_distance : float = 0 # [m]

    charges_count : int = 0 # [u]
