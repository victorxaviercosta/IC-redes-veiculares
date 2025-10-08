import traci
import traci.exceptions

from dataclasses import dataclass

PAR_CHARGE_LEVEL: str = "device.battery.chargeLevel"

@dataclass
class VehState:
    """ Data Class for representing the current state of a vehicle """
    origin: str
    destiny: str
    lowBatteryStart: str

@dataclass
class Reroute:
    """ Data Class for representing a reroute """
    veh_id: str
    original_destiny: str
    new_destiny: str

@dataclass
class LaneData:
    """ Data Class for representing  """
    lane_id: str
    lane_length: float
    visits_count: int


def get_station_postion(station_ID:str) -> tuple[float,float]:
    """ Retruns the absolute position of the given charging station. """

    station_lane_ID: str = traci.chargingstation.getLaneID(station_ID)
    station_pos: str = traci.chargingstation.getParameter(station_ID, "pos")

    # In this case, the "pos" paramenter is specified for the charging station so it is the return value
    if station_pos:
        station_position: tuple[float,float] = (float(station_pos[0]), float(station_pos[1]))

    # In this case there's only the realtive position of the station along the lane, so it's needed to calculate the absolute
    # postion of the station by getting the absolute positions in the lane's shape.
    else:
        lane_shape: list[tuple[float,float]] = traci.lane.getShape(station_lane_ID)
        station_start: float = traci.chargingstation.getStartPos(station_ID)
        
        # Searching at each segment of the lane and calculating the approximate absolute position for the vehicles.
        sub_length: float = 0
        for i in range(len(lane_shape) - 1):
            x0, y0 = lane_shape[i]
            x1, y1 = lane_shape[i+1]

            segment_len: float = ((x0 - x1)**2 + (y0 - y1)**2)**0.5 # Euclidian distance between the points.
            sub_length = sub_length + segment_len

            if station_start <= sub_length:
                # Using Similar Triangles to calculate the approximate position.
                station_position: tuple[float,float] = ( (x0 + (station_start/segment_len) * (x1-x0)),
                                                         (y0 + (station_start/segment_len) * (y1-y0)) )
                break

    return station_position
    

def set_charge_level(veh_ID: str, value: int) -> None:
    """ Set's de battery level of the given vehicle """
    traci.vehicle.setParameter(veh_ID, PAR_CHARGE_LEVEL, str(value))


def get_charge_level(veh_ID: str) -> float:
    """ Get's de battery level of the given vehicle """
    return float(traci.vehicle.getParameter(veh_ID, PAR_CHARGE_LEVEL))
    

def change_vehicle_color(veh_ID: str, charge_level: int, max_battery_capacity: float) -> None:
        """ Changes the given vehicle's color according to it's battery level interpolating between green and red """

        level: float = max(0, min(1, (charge_level / max_battery_capacity)))
        if level < 0.5:
            color: tuple[int] = (255, int(255 * 2 * level), 0)
        else:
            color: tuple[int] = (int(255 * 2 * (1 - level)), 255, 0)

        traci.vehicle.setColor(veh_ID, color)