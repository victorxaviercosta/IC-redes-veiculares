"""
domain/data_types.py
-------------

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
    origin: str
    destiny: str
    low_battery_start: float

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
    """ Capacity is not supported in SUMO by default so it's here simulated by setting the length of the
        charging station accordingly to the fixed size of a vehicle. """

    power: float        # [W]
    efficiency: float   # [0,1]
    capacity: int       # [u] (units, maximum number of vehicles that can charge simultaniosly)
    charge_delay: float # [s] (measured in Simulation's step-length, 1 second by default)
    length: float       # [m]

    @staticmethod
    def getCapacity(cs_id: str) -> int:
        """ Assuming Simulation's definitions that charging station's capacity is incorporated in it's ID in the format: [<id>:<capacity>] """
        try:
            return int( cs_id.split(":")[-1] )
        except:
            return 0


""" Default Charging Station Used to be added at the Simulation """
DEFAULT_CS: ChargingStation = ChargingStation( 
    power = 22_000,
    efficiency = 0.95,
    capacity = 2,
    charge_delay = 5,
    length = 5
)